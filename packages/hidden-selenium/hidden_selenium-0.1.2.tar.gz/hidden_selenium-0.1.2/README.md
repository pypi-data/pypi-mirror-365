# `hidden_selenium` for Python

A stealthy undetected browser automation tool using Selenium.

### Installing

```bash
pip install hidden_selenium
```

### Using

```python
import time
from hidden_selenium import launch_browser

driver = launch_browser()

url = "https://www.browserscan.net"
driver.get(url)

time.sleep(100)
```

### Test

```bash
python test.py
```

Copyright 2025, Max Base
