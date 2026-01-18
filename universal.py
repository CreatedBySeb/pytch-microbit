import os
import pytch

if os.uname().release.startswith("1."):
    pytch.run()
else:
    import microbit_v2