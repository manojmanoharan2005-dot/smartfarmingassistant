#!/usr/bin/env python3
"""
System Health Check for Smart Farming Assistant
Checks dependencies, file structure, and system readiness
"""

import os
import sys
import importlib
import json
from datetime import datetime

def check_system_health():
    """Comprehensive system health check"""
    
    # Console colors
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    
    print(f"\n{BLUE}{BOLD}🔍 Smart Farming Assistant - System Health Check{ENDC}")
    print("=" * 55)
    
    health_score = 0
    max_score = 0
    
    # Check Python version
    print(f"\n{BLUE}🐍 Python Environment:{ENDC}")
    max_score += 1
    if sys.version_info >= (3, 8):
        print(f"{GREEN}✅ Python {sys.version.split()[0]} - Compatible{ENDC}")
        health_score += 1
    else:
        print(f"{RED}❌ Python {sys.version.split()[0]} - Requires Python 3.8+{ENDC}")
    
    # Check required packages
    print(f"\n{BLUE}📦 Required Dependencies:{ENDC}")
    required_packages = [
        'flask', 'pandas', 'numpy', 'scikit-learn', 
        'joblib', 'requests', 'python-dotenv'
    ]
    
    for package in required_packages:
        max_score += 1
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"{GREEN}✅ {package} - Installed{ENDC}")
            health_score += 1
        except ImportError:
            print(f"{RED}❌ {package} - Missing{ENDC}")
    
    # Check directory structure
    print(f"\n{BLUE}📁 Directory Structure:{ENDC}")
    required_dirs = [
        'templates/', 'static/', 'controllers/', 'ml_models/', 
        'data/', 'datasets/', 'utils/', 'models/'
    ]
    
    current_dir = os.getcwd()
    for dir_name in required_dirs:
        max_score += 1
        dir_path = os.path.join(current_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"{GREEN}✅ {dir_name} - Found{ENDC}")
            health_score += 1
        else:
            print(f"{YELLOW}⚠️  {dir_name} - Missing{ENDC}")
    
    # Check critical files
    print(f"\n{BLUE}📄 Critical Files:{ENDC}")
    critical_files = [
        'app.py', 'requirements.txt',
        'ml_models/model_integration.py', 'ml_models/predict.py',
        'data/users.json', 'datasets/Crop_recommendation.csv'
    ]
    
    for file_name in critical_files:
        max_score += 1
        file_path = os.path.join(current_dir, file_name)
        if os.path.exists(file_path):
            print(f"{GREEN}✅ {file_name} - Found{ENDC}")
            health_score += 1
        else:
            print(f"{RED}❌ {file_name} - Missing{ENDC}")
    
    # Check ML models
    print(f"\n{BLUE}🤖 ML Model Status:{ENDC}")
    model_files = [
        'ml_models/crop_recommendation_model.joblib',
        'ml_models/feature_scaler.joblib',
        'models/fertilizer_model.pkl'
    ]
    
    for model_file in model_files:
        max_score += 1
        model_path = os.path.join(current_dir, model_file)
        if os.path.exists(model_path) and os.path.getsize(model_path) > 100:
            print(f"{GREEN}✅ {model_file} - Ready{ENDC}")
            health_score += 1
        elif os.path.exists(model_path):
            print(f"{YELLOW}⚠️  {model_file} - Placeholder (needs training){ENDC}")
        else:
            print(f"{RED}❌ {model_file} - Missing{ENDC}")
    
    # Check data files
    print(f"\n{BLUE}💾 Data Files:{ENDC}")
    data_files = ['users.json', 'crops.json', 'fertilizers.json', 'market_prices.json']
    
    for data_file in data_files:
        max_score += 1
        data_path = os.path.join(current_dir, 'data', data_file)
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    print(f"{GREEN}✅ data/{data_file} - Valid JSON ({len(data)} records){ENDC}")
                    health_score += 1
            except json.JSONDecodeError:
                print(f"{YELLOW}⚠️  data/{data_file} - Invalid JSON{ENDC}")
        else:
            print(f"{RED}❌ data/{data_file} - Missing{ENDC}")
    
    # Calculate health percentage
    health_percentage = (health_score / max_score) * 100 if max_score > 0 else 0
    
    # Print summary
    print(f"\n{BLUE}{BOLD}📊 HEALTH SUMMARY:{ENDC}")
    print("=" * 30)
    
    if health_percentage >= 90:
        status_color = GREEN
        status_emoji = "🟢"
        status_text = "EXCELLENT"
    elif health_percentage >= 70:
        status_color = YELLOW  
        status_emoji = "🟡"
        status_text = "GOOD"
    elif health_percentage >= 50:
        status_color = YELLOW
        status_emoji = "🟠"
        status_text = "FAIR"
    else:
        status_color = RED
        status_emoji = "🔴"
        status_text = "POOR"
    
    print(f"Health Score: {status_color}{health_score}/{max_score} ({health_percentage:.1f}%){ENDC}")
    print(f"System Status: {status_color}{status_emoji} {status_text}{ENDC}")
    
    if health_percentage >= 80:
        print(f"\n{GREEN}🚀 System is ready to run!{ENDC}")
        print(f"{BLUE}💡 Run 'python app.py' to start the application{ENDC}")
    elif health_percentage >= 60:
        print(f"\n{YELLOW}⚠️  System may run with limited functionality{ENDC}")
        print(f"{BLUE}💡 Consider installing missing dependencies{ENDC}")
    else:
        print(f"\n{RED}🛑 System needs attention before running{ENDC}")
        print(f"{BLUE}💡 Install missing dependencies: pip install -r requirements.txt{ENDC}")
    
    print(f"\n{BLUE}📅 Check completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{ENDC}\n")
    
    return health_percentage

if __name__ == "__main__":
    check_system_health()