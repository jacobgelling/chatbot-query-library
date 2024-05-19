#!/usr/bin/env python
"""Provides class to query multiple chatbots with multiple prompts, multiple times, in parallel."""

import asyncio
import os
from .chatbot import _Chatbot, _UnofficialChatbot, Copilot, Gemini, OpenAI, HuggingFace
from multiprocessing import Process
import json
from tqdm import tqdm
import time
import random
import EdgeGPT.EdgeGPT as EdgeGPT

class MultiChatbot:
    def __init__(self, chatbots: list, prompts: list, temp_dir: str = "temp", output_dir: str = "output", output_filename: str = "results.json", runs: int = 1, max_errors: int = 5):
        self.chatbots = chatbots
        self.prompts = prompts
        self.temp_dir = temp_dir
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.runs = runs
        self.max_errors = max_errors

    def query(self):
        """Query the chatbots in parallel."""

        # Create temp and output directories if they do not exist
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

        # Create processes array to run each chatbot query in parallel
        processes = []
        for chatbot in self.chatbots:
            processes.append(Process(target=self._query_chatbot, args=(chatbot, len(processes))))

        # Start each process
        for process in processes:
            process.start()
        
        # Wait for each process to finish
        for process in processes:
            process.join()

        # If the output file already exists, load it
        results = []
        if os.path.exists(os.path.join(self.output_dir, self.output_filename)):
            with open(os.path.join(self.output_dir, self.output_filename), "r") as f:
                results = json.load(f)

        # Combine all temp files into results
        for chatbot in self.chatbots:
            temp_filename = self._temp_filename(chatbot)
            if os.path.exists(temp_filename):
                with open(temp_filename, "r") as f:
                    results += json.load(f)
                os.remove(temp_filename)
        
        # Write results to output file
        with open(os.path.join(self.output_dir, self.output_filename), "w") as f:
            f.write(json.dumps(results))

    def _temp_filename(self, chatbot: _Chatbot) -> str:
        """Return the temp filename for the chatbot.
        
        Args:
            chatbot (_Chatbot): Chatbot object.
            
        Returns:
            str: Temp filename."""
        return os.path.join(self.temp_dir, chatbot.name.lower() + ".json")
    
    def _log_error(self, ex: Exception | str, chatbot: _Chatbot) -> None:
        """Log an error to the chatbot's log file."""
        with open(os.path.join(self.temp_dir, chatbot.name.lower() + ".log"), "a") as f:
            if type(ex) is str:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}: {ex}\n")
            else:
                for error in ex.args:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}: {error}\n")

    def _query_chatbot(self, chatbot: _Chatbot, progress_bar_index: int = None) -> None:
        """
        Query the specified chatbot.
        """

        # If the temp file exists, load it
        temp_filename = self._temp_filename(chatbot)
        temp_results = []
        if os.path.exists(temp_filename):
            with open(temp_filename, "r") as f:
                temp_results = json.load(f)

        # If the output file already exists, load it
        results = []
        if os.path.exists(os.path.join(self.output_dir, self.output_filename)):
            with open(os.path.join(self.output_dir, self.output_filename), "r") as f:
                results = json.load(f)
        
        # Create progress bar
        initial = 0
        for prompt in self.prompts:
            # Count responses for this chatbot in both temp and output files
            temp_count = sum(1 for result in temp_results if result["prompt"] == prompt)
            results_count = sum(1 for result in results if result["prompt"] == prompt and result["chatbot"] == chatbot.name)
            
            # Add the minimum of the counts and runs to initial progress bar value
            initial += min(temp_count, self.runs) + min(results_count, self.runs)
        progress_bar = tqdm(initial=initial, total=len(self.prompts) * self.runs, position=progress_bar_index, desc=chatbot.name)

        # For each prompt
        for prompt in self.prompts:
            # Count responses for this chatbot and prompt in both temp and output files
            prompt_runs = min(sum(1 for result in temp_results if result["prompt"] == prompt), self.runs) + min(sum(1 for result in results if result["prompt"] == prompt and result["chatbot"] == chatbot.name), self.runs)

            # Query multiple times and store the results
            run = 0
            error_count = 0
            while run < self.runs - prompt_runs:
                try:
                    # Rate limit if using unofficial API
                    if isinstance(chatbot, _UnofficialChatbot):
                        time.sleep(random.uniform(15, 45))

                    # Rate limit if a certain number of unhandled errors have occurred in a row
                    if error_count >= self.max_errors:
                        waiting_time = min(error_count - self.max_errors + 1, 10) * random.uniform(55, 65)
                        self._log_error(f"{error_count} unhandled errors have occurred in a row, waiting {round(waiting_time / 60)}m.", chatbot)
                        time.sleep(waiting_time)

                    # Perform query and store in temp results
                    temp_results.append({
                        "timestamp": time.time(),
                        "chatbot": chatbot.name,
                        "prompt": prompt,
                        "temperature": chatbot.temperature_to_string() if type(chatbot.temperature) == EdgeGPT.ConversationStyle else chatbot.temperature,
                        "response": chatbot.query(prompt)
                    })

                    # Save temp results
                    with open(temp_filename, "w") as f:
                        f.write(json.dumps(temp_results))

                    # Run is successful, so update progress bar, run count and error count
                    progress_bar.update(1)
                    run += 1
                    error_count = 0

                except asyncio.TimeoutError as ex:
                    self._log_error(ex, chatbot)
                    error_count += 1
                    continue

                except RuntimeError as ex:
                    self._log_error(ex, chatbot)
                    error_count += 1
                    continue
                
                except Exception as ex:
                    self._log_error(ex, chatbot)

                    # Rate limit by a second if the error is related to rate limiting
                    if isinstance(chatbot, OpenAI) and type(ex.args[0]) is str and "Rate limit reached" in ex.args[0]:
                        time.sleep(1)
                    elif isinstance(chatbot, HuggingFace) and type(ex.args[0]) is str and "Model is overloaded" in ex.args[0]:
                        time.sleep(1)

                    # Immediately kill the cookie file if the error is related to it
                    elif isinstance(chatbot, Gemini) and type(ex.args[0]) is str and "SNlM0e value not found" in ex.args[0]:
                        chatbot.kill_cookie_file()
                    elif isinstance(chatbot, Copilot) and type(ex.args[0]) is str and ("CaptchaChallenge" in ex.args[0] or "Authentication failed" in ex.args[0]):
                        chatbot.kill_cookie_file()

                    # Otherwise, treat as unhandled error
                    else:
                        error_count += 1

                    continue

        # Close progress bar
        progress_bar.close()
