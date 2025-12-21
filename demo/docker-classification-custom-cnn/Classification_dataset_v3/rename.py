import os
import argparse

def rename_images(folder_path, prefix_name, start_index):
    try:
        # Get all files in the folder
        files = sorted(os.listdir(folder_path))  # Sorting ensures consistent order

        image_files = [f for f in files if os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif'))] #Filter for image files

        if not image_files:
            print("No image files found in the specified folder.")
            return

        for i, filename in enumerate(image_files):
            new_index = start_index + i
            new_name = f"{prefix_name}_{new_index:04d}{os.path.splitext(filename)[1]}"  # Format with leading zeros
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name)

            os.rename(old_path, new_path)
            print(f"Renamed '{filename}' to '{new_name}'")

    except FileNotFoundError:
        print(f"Error: Folder '{folder_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    cwd = os.getcwd()
    dataset_path = os.path.join(cwd,"images")
    split_type = "test"
    split_path = os.path.join(dataset_path, split_type)
    class_name = "person"
    full_dataset_path = os.path.join(split_path, class_name)
    rename_images(folder_path=full_dataset_path, prefix_name="person", start_index=2000)