python -m venv telegram-env

# Detect OS
OS=$(uname)

if [[ "$OS" == "Linux" || "$OS" == "Darwin" ]]; then
    echo "Activating virtual environment on Linux/macOS"
    source telegram-env/bin/activate  # Activate on macOS/Linux
elif [[ "$OS" =~ "MINGW" || "$OS" =~ "CYGWIN" ]]; then
    echo "Activating virtual environment on Windows"
    .\telegram-env\Scripts\activate   # Activate on Windows
fi

pip install -r requirements.txt

python ./src/scannerCLI.py
