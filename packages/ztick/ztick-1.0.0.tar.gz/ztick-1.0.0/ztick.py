import time

__version__ = "1.0.0"
__author__ = "M.1XT"
__license__ = "R3"

_SCALE_FACTORS = {
    "s": 1_000_000_000,     
    "ms": 1_000_000,        
    "us": 1_000,            
    "ns": 1,                
    "ps": 1e-3,             
    "fs": 1e-6,             
    "as": 1e-9,             
    "zs": 1e-12,           
    "ys": 1e-15             

_TARGET_WINDOWS_NS = {
    "s": 10_000_000,   
    "ms": 500_000,     
    "us": 10_000,
    "ns": 100,
    "ps": 50,
    "fs": 20,
    "as": 10,
    "zs": 5,
    "ys": 1
}


def ztick(duration: float, scale: str = "us") -> None:

    if scale not in _SCALE_FACTORS:
        raise ValueError(f"Unsupported scale '{scale}'. Use one of: {', '.join(_SCALE_FACTORS)}")

    factor = _SCALE_FACTORS[scale]
    duration_ns = int(duration * factor)

    start_ns = time.time_ns()
    end_ns = start_ns + duration_ns
    window = _TARGET_WINDOWS_NS.get(scale, 1000)

    while True:
        now_ns = time.time_ns()

        if now_ns >= end_ns:
            break

        remaining_ns = end_ns - now_ns

        if remaining_ns > window:
            time.sleep(remaining_ns / 4 / 1_000_000_000)  
