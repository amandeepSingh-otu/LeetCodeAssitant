
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== LeetCode Assistant Setup Script ===${NC}"


if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install it first."
    exit 1
fi

echo -e "\n${GREEN}[1/5] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists."
else
    python3 -m venv venv
    echo "Created 'venv'."
fi


echo -e "\n${GREEN}[2/5] Activating virtual environment...${NC}"
source venv/bin/activate


echo -e "\n${GREEN}[3/5] Installing dependencies...${NC}"
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo "Error: backend/requirements.txt not found!"
    exit 1
fi


echo -e "\n${GREEN}[4/5] Configuring API Key...${NC}"
ENV_FILE="backend/config/.env"
mkdir -p backend/config

if [ -f "$ENV_FILE" ]; then
    echo ".env file already exists."
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ $overwrite =~ ^[Yy]$ ]]; then
        read -p "Enter your Google Gemini API Key: " api_key
        echo "GEMINI_API_KEY=$api_key" > "$ENV_FILE"
        echo "Updated $ENV_FILE"
    fi
else
    read -p "Enter your Google Gemini API Key: " api_key
    echo "GEMINI_API_KEY=$api_key" > "$ENV_FILE"
    echo "Created $ENV_FILE"
fi


echo -e "\n${GREEN}[5/5] Starting Backend Server...${NC}"
echo "Server running at http://127.0.0.1:8000"
echo "Press Ctrl+C to stop."


if [ -d "backend" ]; then
    cd backend
    uvicorn main:app --reload 
else
    echo "Error: 'backend' directory not found. Please run this script from the project root."
    exit 1
fi