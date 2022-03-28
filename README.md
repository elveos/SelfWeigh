# SelfWeigh
Weighbridge HMI/kiosk with PlateRecognizer ANPR and Google Drive integration


## Requirements

This has been tested and currently used on Raspberry Pi 4 with Raspbian 10 (with desktop) with Python 3.7.3. For a basic setup, you will need at least one Raspberry Pi, and at least one IP camera with JPG snapshot or RTSP video stream support.

#### Hardware
- Weighbridge unit with RS232 output
    - Tested with Avery Weigh-Tronix E1205
- USB to RS232 adapter with Prolific PL2303 chip
- Raspberry Pi 4 with MicroSD card
- RPi-compatible touch screen LCD (resistive touch recommended, especially for outdoor units)
- At least one IP camera with IR support
    - Current version supports up to 4 cameras
- Thermal POS printer
    - Tested with Naviatec (Zjiang) 5890T
    - CUPS support required for QR-code printing
- Optional: 1-2 additional RPi-s with touchscreens for outdoor units

## Installation & Configuration
#### Flashing SD card(s)
Download 32-bit [Raspberry Pi OS (Legacy) 10 with desktop](https://www.raspberrypi.com/software/operating-systems/#raspberry-pi-os-legacy) image.

Flash the downloaded image to SD card(s) with a flashing tool, such as [balenaEtcher](https://www.balena.io/etcher/).

### Installation
Once you've set up and booted up Pi, install the necessary packages and Python modules:
```
sudo apt install git sshfs ser2net socat moreutils python3-{pip,tk,pandas,opencv}
python3 -m pip install serial pydrive urllib3 requests expect
```

Clone this repo to ~/SelfWeigh dir and make the necessary files executable:
```
mkdir ~/SelfWeigh; git clone https://github.com/LeoVae/SelfWeigh.git ~/SelfWeigh
cd ~/SelfWeigh/
find ~/SelfWeigh/ -type f \(-name "*.sh" -o name "*.py \)" -exec chmod +x {} \;
```

### Configuration
Make sure that each Pi and camera is using static IP or a hostname.

Enable the SSH server by following [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/computers/remote-access.html#ssh).

Enter your Google API Client ID and Client Secret to ```settings.yaml```.

Complete the necessary configuration in ```settings_main.py```.



#### Main unit configuration

Enable serial port over TCP sharing on the main unit only:
```
echo "3333:raw:0:dev:/tty/USB0:9600 8DATABITS NONE 1STOPBIT max-connections=5" >> /etc/ser2net.conf
systemctl restart ser2net.service
```

Make SelfWeigh start on boot:
```
sudo cp ~/Projects/SelfWeigh/selfweigh-autostart.desktop /etc/xdg/autostart/
chmod +x /etc/xdg/autostart/selfweigh-autostart.desktop
```


#### Configuration for outdoor units only
Generate SSH keypair on outdoor unit and copy it to main unit:
```
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
ssh-copy-id pi@<remote-unit-ip>
```
Set the main unit's IP/hostname in ```launch.sh```:
```
sed -i 's|MAIN_UNIT_IP="empty"|MAIN_UNIT_IP="main-unit-hostname.lan"|g' launch.sh
```

Make SelfWeigh start on boot:
```
sudo cp ~/Projects/SelfWeigh/selfweigh_outdoor-autostart.desktop /etc/xdg/autostart/
chmod +x /etc/xdg/autostart/selfweigh_outdoor-autostart.desktop
```

## To Do: Usage
