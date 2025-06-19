import cv2
import numpy as np
import pyautogui
import datetime
import os
import getpass
import time
from PIL import Image, ImageDraw, ImageFont
import sys

class ScreenRecorder:
    def __init__(self):
        self.username = getpass.getuser()
        self.recording = False
        self.output_folder = f"D:\\{self.username}"
        self.video_writer = None
        
        print(f"Detected username: {self.username}")
        
        # Check and setup output folder
        if not self.setup_output_folder():
            return
        
        # Get screen dimensions
        try:
            self.screen_width, self.screen_height = pyautogui.size()
            print(f"Screen resolution: {self.screen_width}x{self.screen_height}")
        except Exception as e:
            print(f"Error getting screen size: {e}")
            return
        
        # Video settings
        self.fps = 10  # Reduced FPS for better performance
        
        # Create filename with current date and time
        current_time = datetime.datetime.now()
        self.filename = f"{self.username}_{current_time.strftime('%Y%m%d_%H%M%S')}.avi"
        self.filepath = os.path.join(self.output_folder, self.filename)
        
        print(f"Output file: {self.filepath}")
        
        # Initialize video writer with different codecs (try multiple)
        self.init_video_writer()
    
    def setup_output_folder(self):
        """Create output folder if it doesn't exist"""
        try:
            # Check if D drive exists
            if not os.path.exists("D:\\"):
                print("D:\\ drive not found. Using current directory instead.")
                self.output_folder = f".\\{self.username}"
            
            if not os.path.exists(self.output_folder):
                os.makedirs(self.output_folder)
                print(f"Created folder: {self.output_folder}")
            else:
                print(f"Using existing folder: {self.output_folder}")
            return True
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def init_video_writer(self):
        """Initialize video writer with fallback codecs"""
        codecs_to_try = [
            ('XVID', cv2.VideoWriter_fourcc(*'XVID')),
            ('MJPG', cv2.VideoWriter_fourcc(*'MJPG')),
            ('MP4V', cv2.VideoWriter_fourcc(*'mp4v')),
            ('X264', cv2.VideoWriter_fourcc(*'X264'))
        ]
        
        for codec_name, fourcc in codecs_to_try:
            try:
                print(f"Trying codec: {codec_name}")
                self.video_writer = cv2.VideoWriter(
                    self.filepath,
                    fourcc,
                    self.fps,
                    (self.screen_width, self.screen_height)
                )
                
                # Test if the writer is opened successfully
                if self.video_writer.isOpened():
                    print(f"Successfully initialized with {codec_name} codec")
                    return True
                else:
                    self.video_writer.release()
                    
            except Exception as e:
                print(f"Failed to initialize with {codec_name}: {e}")
                continue
        
        print("Error: Could not initialize video writer with any codec")
        return False
    
    def add_watermark(self, frame):
        """Add username and live clock watermark to the frame"""
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
            
            # Add background rectangles for better visibility
            cv2.rectangle(frame, (10, 10), (400, 100), (0, 0, 0), -1)  # Black background
            cv2.rectangle(frame, (10, 10), (400, 100), (255, 255, 255), 2)  # White border
            
            # Add text
            cv2.putText(frame, username_text, username_pos, font, font_scale, color, thickness)
            cv2.putText(frame, time_text, time_pos, font, font_scale, color, thickness)
            
            return frame
        except Exception as e:
            print(f"Error adding watermark: {e}")
            return frame
    
    def record_screen(self):
        """Main recording function"""
        if self.video_writer is None or not self.video_writer.isOpened():
            print("Error: Video writer not initialized properly")
            return
        
        print("Starting screen recording...")
        print("Press Ctrl+C to stop recording")
        
        self.recording = True
        frame_count = 0
        
        try:
            # Disable pyautogui failsafe
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
                    
                    # Print progress every 50 frames
                    if frame_count % 50 == 0:
                        print(f"Recorded {frame_count} frames...")
                    
                    # Control frame rate
                    time.sleep(1/self.fps)
                    
                except Exception as e:
                    print(f"Error capturing frame: {e}")
                    break
                    
        except KeyboardInterrupt:
            print(f"\nRecording stopped by user after {frame_count} frames")
        except Exception as e:
            print(f"Error during recording: {e}")
        finally:
            self.stop_recording()
    
    def stop_recording(self):
        """Stop recording and cleanup"""
        self.recording = False
        if self.video_writer:
            self.video_writer.release()
        cv2.destroyAllWindows()
        
        print(f"\nRecording saved to: {self.filepath}")
        
        # Check if file was created and show file size
        if os.path.exists(self.filepath):
            file_size = os.path.getsize(self.filepath)
            if file_size > 0:
                print(f"File size: {file_size / (1024 * 1024):.2f} MB")
                print("Recording completed successfully!")
            else:
                print("Warning: Output file is empty (0 bytes)")
        else:
            print("Error: Output file was not created")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'pyautogui': 'pyautogui'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {pip_name} is installed")
        except ImportError:
            missing_packages.append(pip_name)
            print(f"✗ {pip_name} is NOT installed")
    
    if missing_packages:
        print(f"\nPlease install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main function to run the screen recorder"""
    print("=== Screen Recorder with Watermark ===")
    print("Checking dependencies...")
    
    if not check_dependencies():
        return
    
    print("\nAll dependencies are installed!")
    print("Initializing screen recorder...")
    
    try:
        # Create recorder instance
        recorder = ScreenRecorder()
        
        # Check if initialization was successful
        if recorder.video_writer is None:
            print("Failed to initialize recorder. Please check the error messages above.")
            return
        
        # Start recording
        print("\nStarting recording in 3 seconds...")
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        print("Recording started!")
        recorder.record_screen()
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
