export const AKRA_TOUCH_FEEDBACK_EVENT_NAME = "akra-trader:haptic-feedback";
export const AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION = 1;
export const AKRA_TOUCH_FEEDBACK_WEBKIT_HANDLER = "akraTouchFeedback";
const AKRA_TOUCH_FEEDBACK_IMPACT_DURATION_MS = 18;

export type AkraTouchFeedbackDetail = {
  anchorGapWindowKey: string;
  effect: "impact";
  impactStyle: "light";
  source: "gap-window-picker-sweep-activation";
  trigger: "touch-hold";
};

export type AkraTouchFeedbackEnvelope = {
  detail: AkraTouchFeedbackDetail;
  type: typeof AKRA_TOUCH_FEEDBACK_EVENT_NAME;
  version: typeof AKRA_TOUCH_FEEDBACK_BRIDGE_VERSION;
};

type ReactNativeWebViewBridge = {
  postMessage?: (message: string) => void;
};

type TelegramWebAppBridge = {
  HapticFeedback?: {
    impactOccurred?: (style: "light" | "medium" | "heavy" | "rigid" | "soft") => void;
  };
};

type WebkitTouchFeedbackBridge = {
  postMessage?: (payload: AkraTouchFeedbackEnvelope) => void;
};

type PlatformTouchFeedbackBridge = {
  ReactNativeWebView?: ReactNativeWebViewBridge;
  Telegram?: {
    WebApp?: TelegramWebAppBridge;
  };
  webkit?: {
    messageHandlers?: {
      akraTouchFeedback?: WebkitTouchFeedbackBridge;
    };
  };
  __AKRA_TOUCH_FEEDBACK_HOST_SHIMS_INSTALLED__?: boolean;
};

function triggerLocalTouchImpact() {
  if (typeof navigator === "undefined" || typeof navigator.vibrate !== "function") {
    return;
  }
  try {
    navigator.vibrate?.(AKRA_TOUCH_FEEDBACK_IMPACT_DURATION_MS);
  } catch {
    // Ignore unsupported or blocked vibration calls.
  }
}

function dispatchAkraTouchFeedbackReceipt(envelope: AkraTouchFeedbackEnvelope, bridge: string) {
  try {
    window.dispatchEvent(
      new CustomEvent<{
        bridge: string;
        envelope: AkraTouchFeedbackEnvelope;
      }>(`${AKRA_TOUCH_FEEDBACK_EVENT_NAME}:received`, {
        detail: {
          bridge,
          envelope,
        },
      }),
    );
  } catch {
    // Ignore custom-event failures inside constrained host shells.
  }
}

function handleAkraTouchFeedbackEnvelope(envelope: AkraTouchFeedbackEnvelope, bridge: string) {
  triggerLocalTouchImpact();
  dispatchAkraTouchFeedbackReceipt(envelope, bridge);
}

function installAkraTouchFeedbackWebkitReceiver(platformBridge: PlatformTouchFeedbackBridge) {
  platformBridge.webkit ??= {};
  platformBridge.webkit.messageHandlers ??= {};
  if (platformBridge.webkit.messageHandlers[AKRA_TOUCH_FEEDBACK_WEBKIT_HANDLER]) {
    return;
  }
  platformBridge.webkit.messageHandlers[AKRA_TOUCH_FEEDBACK_WEBKIT_HANDLER] = {
    postMessage: (payload) => {
      handleAkraTouchFeedbackEnvelope(payload, "webkit");
    },
  };
}

function installAkraTouchFeedbackReactNativeReceiver(platformBridge: PlatformTouchFeedbackBridge) {
  if (platformBridge.ReactNativeWebView) {
    return;
  }
  platformBridge.ReactNativeWebView = {
    postMessage: (message) => {
      try {
        const parsed = JSON.parse(message) as AkraTouchFeedbackEnvelope;
        handleAkraTouchFeedbackEnvelope(parsed, "react-native-webview");
      } catch {
        // Ignore malformed host shim payloads.
      }
    },
  };
}

function installAkraTouchFeedbackEventReceiver() {
  const eventTarget = window as Window;
  const listener = (event: Event) => {
    const customEvent = event as CustomEvent<AkraTouchFeedbackEnvelope>;
    if (!customEvent.detail) {
      return;
    }
    handleAkraTouchFeedbackEnvelope(customEvent.detail, "window-event");
  };
  eventTarget.addEventListener(AKRA_TOUCH_FEEDBACK_EVENT_NAME, listener);
}

export function installAkraTouchFeedbackHostReceivers() {
  const platformBridge = window as Window & typeof globalThis & PlatformTouchFeedbackBridge;
  if (platformBridge.__AKRA_TOUCH_FEEDBACK_HOST_SHIMS_INSTALLED__) {
    return;
  }
  installAkraTouchFeedbackWebkitReceiver(platformBridge);
  installAkraTouchFeedbackReactNativeReceiver(platformBridge);
  installAkraTouchFeedbackEventReceiver();
  platformBridge.__AKRA_TOUCH_FEEDBACK_HOST_SHIMS_INSTALLED__ = true;
}

export function triggerAkraTouchFeedbackBridge(envelope: AkraTouchFeedbackEnvelope) {
  const platformBridge = window as Window & typeof globalThis & PlatformTouchFeedbackBridge;
  let usedPlatformFeedbackBridge = false;
  const telegramHaptics = platformBridge.Telegram?.WebApp?.HapticFeedback;
  if (typeof telegramHaptics?.impactOccurred === "function") {
    try {
      telegramHaptics.impactOccurred("light");
      usedPlatformFeedbackBridge = true;
    } catch {
      // Ignore Telegram bridge failures and continue through fallbacks.
    }
  }
  if (!usedPlatformFeedbackBridge) {
    const handler =
      platformBridge.webkit?.messageHandlers?.[AKRA_TOUCH_FEEDBACK_WEBKIT_HANDLER];
    if (typeof handler?.postMessage === "function") {
      try {
        handler.postMessage(envelope);
        usedPlatformFeedbackBridge = true;
      } catch {
        // Ignore failing handlers and keep probing fallbacks.
      }
    }
  }
  if (
    !usedPlatformFeedbackBridge
    && typeof platformBridge.ReactNativeWebView?.postMessage === "function"
  ) {
    try {
      platformBridge.ReactNativeWebView.postMessage(JSON.stringify(envelope));
      usedPlatformFeedbackBridge = true;
    } catch {
      // Ignore React Native host bridge failures and continue through fallbacks.
    }
  }
  if (!usedPlatformFeedbackBridge) {
    try {
      window.dispatchEvent(
        new CustomEvent<AkraTouchFeedbackEnvelope>(AKRA_TOUCH_FEEDBACK_EVENT_NAME, {
          detail: envelope,
        }),
      );
      usedPlatformFeedbackBridge = true;
    } catch {
      // Ignore custom-event bridge failures and continue through fallbacks.
    }
  }
  if (!usedPlatformFeedbackBridge) {
    triggerLocalTouchImpact();
  }
}
