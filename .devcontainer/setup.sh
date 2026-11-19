#!/bin/bash
set -e
sudo apt-get update
sudo apt-get install -y xvfb x11vnc novnc websockify fluxbox fonts-noto-cjk wget
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

cat > ~/start-browser.sh << 'EOF'
#!/bin/bash
pkill -f Xvfb 2>/dev/null; pkill -f x11vnc 2>/dev/null; pkill -f websockify 2>/dev/null
Xvfb :1 -screen 0 1280x800x24 &
sleep 2
export DISPLAY=:1
fluxbox &
x11vnc -display :1 -forever -shared -nopw -rfbport 5900 -quiet &
websockify --web /usr/share/novnc 6080 localhost:5900 &
google-chrome --no-sandbox --start-maximized --lang=ja https://www.google.com &
echo "ブラウザ準備完了: ポート6080のPORTSタブから開いてください"
EOF
chmod +x ~/start-browser.sh
