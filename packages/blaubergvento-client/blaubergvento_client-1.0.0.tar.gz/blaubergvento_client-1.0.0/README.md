# Introduction

This is a Python module for communicating with a Blauberg Vento (and OEMS like Duka One S6w).
The Blauberg Vento is a one room ventilationsystem with a heat exchanger.

This module has roots in the [dukaonesdk](https://github.com/dingusdk/dukaonesdk/blob/master/readme.md) but has been rewritten from scratch in order to better separate 
responsibilities into different classes, while still being able to reuse shared logic.

The primary goal for this module is to create a Python client that makes communicating with Blauberg 
Vento(and its derivatives) a simple task. 

## Installation
```
python3 -m pip install blaubergvento_client
```

The module has the following 2 levels of communication:
1. A low level client that implements the communication protocol specified by Blauberg.
2. A high level client that utilizes the protocol client for easier usage.
 
## Protocol Client Example 

```
async def main():
    resource = Client()

    # 1. List devices (first page, 20 per page)
    devices = await resource.find_all(page=0, size=20)
    print(f"Total devices returned: {len(devices)}")
    for device in devices:

        print(f"Device ID: {device.id}, IP: Do-no, Mode: {device.mode}, Speed: {device.speed}")

    # 2. Find a specific device by ID
    device_id = devices[0].id if devices else None
    if device_id:
        device = await resource.find_by_id(device_id)
        print(f"\nDetails of device {device_id}: Mode={device.mode}, Speed={device.speed}")

        # 3. Modify device properties and save
        device.speed = Speed.HIGH
        updated_device = await resource.save(device)
        print(f"Updated device speed: {updated_device.speed}")

if __name__ == "__main__":
    asyncio.run(main())
```

## High Level Example

```
async def main():
    print("Searching for Blauberg Vento devices on the network...")

    client = ProtocolClient(timeout=2.0)  # Increase timeout if needed
    devices = await client.find_devices()

    if not devices:
        print("No devices found.")
    else:
        print(f"Found {len(devices)} device(s):")
        for idx, device in enumerate(devices, start=1):
            print(f"{idx}. ID: {device.id}, IP: {device.ip}")

if __name__ == "__main__":
    asyncio.run(main())

```

[You can see the documentation from Blauberg here](https://blaubergventilatoren.de/uploads/download/b133_4_1en_01preview.pdf)
