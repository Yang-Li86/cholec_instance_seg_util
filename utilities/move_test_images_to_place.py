import os
import shutil
from pathlib import Path

def move_test_images_to_folders(testset_images_dir, test_dataset_path):
    """
    Move test images from testset_images directory to appropriate test video folders
    
    Args:
        testset_images_dir: Path to testset_images directory containing all test images
        test_dataset_path: Path to test folder in cholecinstanceseg_reference_image_and_annotations
    """
    
    if not os.path.exists(testset_images_dir):
        print(f"Error: {testset_images_dir} does not exist")
        return
    
    if not os.path.exists(test_dataset_path):
        print(f"Error: {test_dataset_path} does not exist")
        return
    
    # Get all image files from testset_images
    image_files = [f for f in os.listdir(testset_images_dir) if f.endswith('.png')]
    print(f"Found {len(image_files)} images in testset_images")
    
    # Get all test video folders
    test_folders = [f for f in os.listdir(test_dataset_path) 
                   if os.path.isdir(os.path.join(test_dataset_path, f)) and f.startswith('VID')]
    
    print(f"Found {len(test_folders)} test video folders")
    
    moved_count = 0
    not_matched = []
    
    # Process each image file
    for image_file in image_files:
        # Extract video identifier from image filename
        # Examples: seg8k_video09_000832.png, t50_VID78_000030.png, t80_VID33_000000.png
        
        matched = False
        
        # Try different naming patterns
        if image_file.startswith('seg8k_video'):
            # Format: seg8k_video09_000832.png
            parts = image_file.split('_')
            if len(parts) >= 2:
                video_num = parts[1].replace('video', '')  # Extract "09" from "video09"
                try:
                    vid_num = int(video_num)
                    target_folder = f"VID{vid_num:02d}_seg8k"
                except ValueError:
                    continue
                    
        elif image_file.startswith('t50_VID') or image_file.startswith('t80_VID'):
            # Format: t50_VID78_000030.png or t80_VID33_000000.png
            parts = image_file.split('_')
            if len(parts) >= 2:
                vid_part = parts[1]  # "VID78"
                vid_num_str = vid_part.replace('VID', '')
                dataset_type = parts[0]  # "t50" or "t80"
                try:
                    vid_num = int(vid_num_str)
                    if dataset_type == 't50':
                        # Could be either t50_full or t50_sparse, check which exists
                        target_folder_full = f"VID{vid_num:02d}_t50_full"
                        target_folder_sparse = f"VID{vid_num:02d}_t50_sparse"
                        
                        if target_folder_full in test_folders:
                            target_folder = target_folder_full
                        elif target_folder_sparse in test_folders:
                            target_folder = target_folder_sparse
                        else:
                            continue
                    else:  # t80
                        target_folder = f"VID{vid_num:02d}_t80_sparse"
                except ValueError:
                    continue
        else:
            # Unknown format
            not_matched.append(image_file)
            continue
        
        # Check if target folder exists
        if target_folder in test_folders:
            # Create img_dir if it doesn't exist
            target_path = os.path.join(test_dataset_path, target_folder, 'img_dir')
            os.makedirs(target_path, exist_ok=True)
            
            # Move the image
            source_path = os.path.join(testset_images_dir, image_file)
            dest_path = os.path.join(target_path, image_file)
            
            try:
                shutil.copy2(source_path, dest_path)  # Use copy2 to preserve metadata
                print(f"  ✓ Moved: {image_file} → {target_folder}/img_dir/")
                moved_count += 1
                matched = True
            except Exception as e:
                print(f"  ✗ Error moving {image_file}: {str(e)}")
        
        if not matched:
            not_matched.append(image_file)
    
    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total images processed: {len(image_files)}")
    print(f"Successfully moved: {moved_count}")
    print(f"Not matched: {len(not_matched)}")
    
    if not_matched:
        print(f"\nImages that couldn't be matched:")
        for img in not_matched[:10]:  # Show first 10
            print(f"  - {img}")
        if len(not_matched) > 10:
            print(f"  ... and {len(not_matched) - 10} more")

def analyze_test_images_and_folders(testset_images_dir, test_dataset_path):
    """
    Analyze the naming patterns to help debug matching issues
    """
    print("=== ANALYSIS ===")
    
    # Analyze image naming patterns
    image_files = [f for f in os.listdir(testset_images_dir) if f.endswith('.png')]
    print(f"\nSample image filenames:")
    for img in image_files[:10]:
        print(f"  {img}")
    
    # Analyze test folder names
    test_folders = [f for f in os.listdir(test_dataset_path) 
                   if os.path.isdir(os.path.join(test_dataset_path, f)) and f.startswith('VID')]
    print(f"\nTest folders available:")
    for folder in sorted(test_folders):
        print(f"  {folder}")
    
    # Count by pattern
    seg8k_count = sum(1 for img in image_files if img.startswith('seg8k_video'))
    t50_count = sum(1 for img in image_files if img.startswith('t50_VID'))
    t80_count = sum(1 for img in image_files if img.startswith('t80_VID'))
    other_count = len(image_files) - seg8k_count - t50_count - t80_count
    
    print(f"\nImage pattern counts:")
    print(f"  seg8k_video*: {seg8k_count}")
    print(f"  t50_VID*: {t50_count}")
    print(f"  t80_VID*: {t80_count}")
    print(f"  Other patterns: {other_count}")

# Usage
testset_images_dir = "/home/yang/Downloads/instance_seg_dataset/testset_images"
test_dataset_path = "/home/yang/Downloads/instance_seg_dataset/cholecinstanceseg_reference_image_and_annotations/test"

# First, analyze the patterns
analyze_test_images_and_folders(testset_images_dir, test_dataset_path)

print("\n" + "="*50)
print("MOVING IMAGES...")
print("="*50)

# Then move the images
move_test_images_to_folders(testset_images_dir, test_dataset_path)