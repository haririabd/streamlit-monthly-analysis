import os
import glob
import re
import pandas as pd

def parse_email_text(text):
    """
    Uses Regular Expressions to find the specific values between the known text markers.
    """
    # 1. SiteID: Look for "SiteID - " and grab all non-whitespace characters after it
    site_id_match = re.search(r"SiteID\s*-\s*(\S+)", text)
    site_id = site_id_match.group(1) if site_id_match else None

    # 2. SiteName: Look for "SiteName - " and grab all non-whitespace characters
    site_name_match = re.search(r"SiteName\s*-\s*(\S+)", text)
    site_name = site_name_match.group(1) if site_name_match else None

    # 3. Region: Look for "Region - ", grab everything until the word "Polygon"
    region_match = re.search(r"Region\s*-\s*(.*?)\s*Polygon", text)
    region = region_match.group(1).strip() if region_match else None

    # 4. State: Look for "State - ", grab everything until the word "District"
    state_match = re.search(r"State\s*-\s*(.*?)\s*District", text)
    state = state_match.group(1).strip() if state_match else None

    return {
        "SiteID": site_id,
        "SiteName": site_name,
        "Region": region,
        "State": state
    }

def process_txt_to_excel():
    # --- CONFIGURATION ---
    folder_path = r"C:"  # Change to your text files folder
    output_excel_path = r"C:"
    # ---------------------

    search_pattern = os.path.join(folder_path, "*.txt")
    file_list = glob.glob(search_pattern)
    
    print(f"Found {len(file_list)} text files. Starting extraction...\n")

    extracted_data_list = []
    success_count = 0
    error_count = 0

    for file_path in file_list:
        try:
            filename = os.path.basename(file_path)
            
            # Read the text file
            with open(file_path, 'r', encoding='utf-8') as f:
                email_body = f.read()
            
            # flatten text to remove newline
            email_body = email_body.replace('\n', ' ').replace('\r', ' ')
            
            # Parse the text using our regex function
            parsed_data = parse_email_text(email_body)
            
            # Add the filename just for traceability
            parsed_data["SourceFile"] = filename 
            
            # Append to our master list
            extracted_data_list.append(parsed_data)
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            error_count += 1

    # Convert the list of dictionaries into a pandas DataFrame
    if extracted_data_list:
        df = pd.DataFrame(extracted_data_list)
        
        # Save to Excel
        df.to_excel(output_excel_path, index=False)
        print(f"\n✅ Finished!")
        print(f"Successfully extracted data from {success_count} files.")
        print(f"Saved Excel file to: {output_excel_path}")
    else:
        print("\n⚠️ No data was extracted. Check your folder path and text file contents.")

if __name__ == "__main__":
    process_txt_to_excel()