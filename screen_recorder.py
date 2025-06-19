import cv2
import numpy as np
import pyautogui
import datetime
import os
import getpass
import time
from PIL import Image, ImageDraw, ImageFont
import sys
import logging
import threading
import signal

class AutoScreenRecorder:
    def __init__(self):
        self.username = getpass.getuser()
        self.recording = False
        self.output_folder = f"D:\\ScreenRecordings\\{self.username}"
        self.video_writer = None
        self.setup_logging()
        
        # Wait for system to fully load after login
        time.sleep(30)  # 30 second delay after login
        
        self.log(f"Auto-recorder started for user: {self.username}")
        
        # Check and setup output folder
        if not self.setup_output_folder():
            return
        
        # Get screen dimensions
        try:
            self.screen_width, self.screen_height = pyautogui.size()
            self.log(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            self.log(f"Error getting screen size: {e}")
            return
        
        # Video settings
        self.fps = 10
        
        # Create filename with current date and time
        current_time = datetime.datetime.now()
        self.filename = f"{self.username}_{current_time.strftime('%Y-%m-%d_%H-%M-%S')}.avi"
        self.filepath = os.path.join(self.output_folder, self.filename)
        
        self.log(f"Output file: {self.filepath}")
        
        # Initialize video writer
        self.init_video_writer()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Setup logging to file"""
        log_dir = f"D:\\ScreenRecordings\\Logs"
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except:
                log_dir = "."  # Use current directory if D drive not available
        
        log_file = os.path.join(log_dir, f"screen_recorder_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()  # Also log to console
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message):
        """Log message"""
        self.logger.info(message)
    
    def setup_output_folder(self):
        """Create output folder if it doesn't exist"""
        try:
            # Check if D drive exists
            if not os.path.exists("D:\\"):
                self.log("D:\\ drive not found. Using Documents folder instead.")
                documents_path = os.path.join(os.path.expanduser("~"), "Documents")
                self.output_folder = os.path.join(documents_path, "ScreenRecordings", self.username)
            
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
                self.log(f"Created folder: {self.output_folder}")
            else:
                self.log(f"Using existing folder: {self.output_folder}")
            return True
        except Exception as e:
            self.log(f"Error creating folder: {e}")
            return False
    
    def init_video_writer(self):
        """Initialize video writer with fallback codecs"""
        codecs_to_try = [
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
            ('MP4V', cv2.VideoWriter_fourcc(*'mp4v'))
        ]
        
        for codec_name, fourcc in codecs_to_try:
            try:
                self.log(f"Trying codec: {codec_name}")
                self.video_writer = cv2.VideoWriter(
                    self.filepath,
                    fourcc,
                    self.fps,
                    (self.screen_width, self.screen_height)
                )
                
                if self.video_writer.isOpened():
                    self.log(f"Successfully initialized with {codec_name} codec")
                    return True
                else:
                    self.video_writer.release()
                    
            except Exception as e:
                self.log(f"Failed to initialize with {codec_name}: {e}")
                continue
        
        self.log("Error: Could not initialize video writer with any codec")
        return False
    
    def add_watermark(self, frame):
        """Add transparent username and live clock watermark to the frame"""
        try:
            # Get current time
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Watermark text
            username_text = f"User: {self.username}"
            time_text = f"Time: {current_time}"
            
            # Font settings
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (255, 255, 255)  # White text
            thickness = 2
            
            # Position watermarks
            username_pos = (20, 40)
            time_pos = (20, 80)
            
            # Create a transparent overlay
            overlay = frame.copy()
            alpha = 0.3  # Transparency level
            
            # Add semi-transparent background rectangle
            cv2.rectangle(overlay, (10, 10), (400, 100), (0, 0, 0), -1)
            
            # Blend the overlay with the original frame for transparency
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            # Add transparent text
            text_overlay = frame.copy()
            cv2.putText(text_overlay, username_text, username_pos, font, font_scale, color, thickness)
            cv2.putText(text_overlay, time_text, time_pos, font, font_scale, color, thickness)
            
            # Blend text with transparency
            text_alpha = 0.7
            cv2.addWeighted(text_overlay, text_alpha, frame, 1 - text_alpha, 0, frame)
            
            return frame
        except Exception as e:
            self.log(f"Error adding watermark: {e}")
            return frame
    
    def record_screen(self):
        """Main recording function"""
        if self.video_writer is None or not self.video_writer.isOpened():
            self.log("Error: Video writer not initialized properly")
            return
        
        self.log("Starting automatic screen recording...")
        self.recording = True
        frame_count = 0
        last_log_time = time.time()
        
        try:
            pyautogui.FAILSAFE = False
            
            while self.recording:
                try:
                    # Capture screenshot
                    screenshot = pyautogui.screenshot()
                    
                    # Convert PIL image to numpy array
                    frame = np.array(screenshot)
                    
                    # Convert RGB to BGR for OpenCV
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    # Add watermark
                    watermarked_frame = self.add_watermark(frame)
                    
                    # Write frame to video
                    self.video_writer.write(watermarked_frame)
                    
                    frame_count += 1
                    
                    # Log progress every 5 minutes (3000 frames at 10fps)
                    current_time = time.time()
                    if current_time - last_log_time >= 300:  # 5 minutes
                        self.log(f"Recording in progress... {frame_count} frames captured")
                        last_log_time = current_time
                    
                    # Control frame rate
                    time.sleep(1/self.fps)
                    
                except Exception as e:
                    self.log(f"Error capturing frame: {e}")
                    time.sleep(1)  # Wait a bit before retrying
                    continue
                    
        except Exception as e:
            self.log(f"Error during recording: {e}")
        finally:
            self.stop_recording()
    
    def stop_recording(self):
        """Stop recording and cleanup"""
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        
        self.log(f"Recording saved to: {self.filepath}")
        
        # Check if file was created and show file size
        if os.path.exists(self.filepath):
            file_size = os.path.getsize(self.filepath)
            if file_size > 0:
                self.log(f"File size: {file_size / (1024 * 1024):.2f} MB")
                self.log("Recording completed successfully!")
            else:
                self.log("Warning: Output file is empty (0 bytes)")
        else:
            self.log("Error: Output file was not created")
    
    def signal_handler(self, signum, frame):
        """Handle system shutdown signals"""
        self.log(f"Received signal {signum}, stopping recording...")
        self.recording = False

def main():
    """Main function for auto-start recording"""
    try:
        # Create recorder instance
        recorder = AutoScreenRecorder()
        
        # Check if initialization was successful
        if recorder.video_writer is None:
            recorder.log("Failed to initialize recorder.")
            return
        
        # Start recording automatically
        recorder.log("Auto-recording will start now...")
        recorder.record_screen()
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        logging.error(traceback.format_exc())

if __name__ == "__main__":
    main()
