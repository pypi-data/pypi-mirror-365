# snz-movie-recsys/intro.py
# -*- coding: utf-8 -*-
import sys
import time
import os

ASCII_LOGO = r"""
░███     ░███   ░██████   ░██    ░██ ░██████░██████████                
░████   ░████  ░██   ░██  ░██    ░██   ░██  ░██                        
░██░██ ░██░██ ░██     ░██ ░██    ░██   ░██  ░██                        
░██ ░████ ░██ ░██     ░██ ░██    ░██   ░██  ░█████████                 
░██  ░██  ░██ ░██     ░██  ░██  ░██    ░██  ░██                        
░██       ░██  ░██   ░██    ░██░██     ░██  ░██                        
░██       ░██   ░██████      ░███    ░██████░██████████                
                                                                       
                                                                       
                                                                       
░█████████  ░██████████   ░██████    ░██████   ░██     ░██   ░██████   
░██     ░██ ░██          ░██   ░██  ░██   ░██   ░██   ░██   ░██   ░██  
░██     ░██ ░██         ░██        ░██           ░██ ░██   ░██         
░█████████  ░█████████  ░██         ░████████     ░████     ░████████  
░██   ░██   ░██         ░██                ░██     ░██             ░██ 
░██    ░██  ░██          ░██   ░██  ░██   ░██      ░██      ░██   ░██  
░██     ░██ ░██████████   ░██████    ░██████       ░██       ░██████   
                                                                       
                                                                       
"""

DESCRIPTION = """
🤖 LangGraph Chatbot CLI
-----------------------------------------
🔹 LangChain + OpenAI + Tavily 기반 챗봇
🔹 실시간 Tool Calling + 상태 기반 대화 흐름
🔹 pip install 후 직접 실행 가능!

사용하려면: 
    python -m langgraph_chatbot.cli

"""

def show_intro():
    os.system("clear" if os.name == "posix" else "cls")
    print(ASCII_LOGO)
    time.sleep(0.2)
    print(DESCRIPTION)
    time.sleep(0.5)
    

if __name__ == "__main__":
    main()