import datetime

def log_run_details(script_name, book_title, runtime):
    """
    Log the run details to run_details.txt, converting runtime from seconds to MM:SS format.
    
    Args:
        script_name (str): Name of the Python script.
        book_title (str): Book title provided by the user.
        runtime (float): Time taken to run the script in seconds.
    """
    try:
        # Convert runtime (seconds) to minutes and seconds
        minutes, seconds = divmod(int(runtime), 60)
        runtime_str = f"{minutes:02d}:{seconds:02d}"
        
        # Get current date and time
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Format the log entry
        log_entry = f"Date: {current_time}, Script: {script_name}, Book Title: {book_title}, Runtime: {runtime_str} (minutes:seconds)\n"
        # Append to run_details.txt
        with open("run_details.txt", "a") as log_file:
            log_file.write(log_entry)
    except Exception as e:
        print(f"Error writing to run_details.txt: {e}")