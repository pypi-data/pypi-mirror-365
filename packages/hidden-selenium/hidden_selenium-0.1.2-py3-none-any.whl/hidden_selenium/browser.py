import random
import time
import undetected_chromedriver as uc

def launch_browser(url=None, wait_time=0):
    gpu_fingerprints = [
        ("Google Inc.", "ANGLE (Qualcomm, Adreno (TM) 740)"),
    ]
    vendor, renderer = random.choice(gpu_fingerprints)

    options = uc.ChromeOptions()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    options.add_argument("--user-agent=" + user_agent)
    options.add_argument("--window-size=412,915")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = uc.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": f"""
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) return "{vendor}";
                if (parameter === 37446) return "{renderer}";
                return getParameter.call(this, parameter);
            }};
        """
    })

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": f"""
            Object.defineProperty(navigator, 'platform', {{
                get: () => 'Linux armv8l'
            }});
            Object.defineProperty(navigator, 'userAgent', {{
                get: () => '{user_agent}'
            }});
            Object.defineProperty(navigator, 'vendor', {{
                get: () => 'Google Inc.'
            }});
            Object.defineProperty(navigator, 'oscpu', {{
                get: () => 'Android'
            }});
        """
    })

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            const originalRTCPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection;
            if (originalRTCPeerConnection) {
                window.RTCPeerConnection = function(...args) {
                    const pc = new originalRTCPeerConnection({
                        iceServers: [{ urls: ["stun:stun.l.google.com:19302"] }],
                        iceTransportPolicy: "relay"
                    });
                    return pc;
                };
            }
        """
    })

    if url:
        driver.get(url)
        if wait_time > 0:
            time.sleep(wait_time)

    return driver
