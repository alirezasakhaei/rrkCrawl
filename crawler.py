import time
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import geckodriver_autoinstaller

# Regex to remove HTML tags
TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    text = text.replace('&nbsp;', ' ')
    return TAG_RE.sub('', text)

# Updated function to find contexts based on start words
def extract_all_phrase_contexts(text, phrase, start_words=["آقای", "خانم"], words_after=5, fallback_words_before=10):
    contexts = []
    try:
        # Clean text once
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        # Create padded versions for reliable searching
        padded_start_words = [f" {word} " for word in start_words]

        # Find all occurrences of the main phrase
        for phrase_match in re.finditer(re.escape(phrase), cleaned_text, re.IGNORECASE):
            phrase_start_index = phrase_match.start()
            phrase_end_index = phrase_match.end()
            text_before_phrase = cleaned_text[:phrase_start_index]

            # Find the last occurrence of any start word before the phrase
            best_start_word_index = -1
            for i, padded_word in enumerate(padded_start_words):
                found_index = text_before_phrase.rfind(padded_word)
                if found_index > best_start_word_index:
                    best_start_word_index = found_index
                    # Adjust index to get the actual word start (remove leading space)
                    best_start_word_index += 1

            context_start_index = -1
            if best_start_word_index != -1:
                context_start_index = best_start_word_index
                print(f"    DEBUG: Found start word ('{cleaned_text[best_start_word_index:best_start_word_index+4]}...') before phrase.")
            else:
                # Fallback: approximate start based on words if no start word found
                print(f"    DEBUG: No start word found before phrase. Using fallback words: {fallback_words_before}")
                words_in_before_text = text_before_phrase.split()
                fallback_start_word_num = max(0, len(words_in_before_text) - fallback_words_before)
                # Try to find the start index of that word in the original cleaned text
                if fallback_start_word_num < len(words_in_before_text):
                     # This is approximate, joining words back might not match original spacing
                     approx_start_phrase = " ".join(words_in_before_text[fallback_start_word_num:])
                     # Search for the beginning of this approximate phrase near the end of text_before_phrase
                     search_start_fallback = max(0, phrase_start_index - len(approx_start_phrase) - 50) # Search window
                     context_start_index = cleaned_text.find(words_in_before_text[fallback_start_word_num], search_start_fallback, phrase_start_index)
                     if context_start_index == -1: context_start_index = max(0, phrase_start_index - 70) # Final fallback: char count
                else:
                     context_start_index = max(0, phrase_start_index - 70) # Fallback: char count if few/no words before

            # Capture text from calculated start up to the end of the phrase
            context_part1 = cleaned_text[context_start_index:phrase_end_index]

            # Capture words after the phrase using regex
            text_after_phrase = cleaned_text[phrase_end_index:]
            pattern_after = rf'^(\s*(?:\S+\s*){{0,{words_after}}})' # Match from beginning of the after-text
            match_after = re.search(pattern_after, text_after_phrase)
            context_part2 = match_after.group(1).strip() if match_after else ""

            # Combine parts
            final_context = (context_part1 + " " + context_part2).strip()
            if final_context:
                 print(f"    DEBUG: Combined context: '{final_context}'")
                 contexts.append(final_context)

    except Exception as e:
        print(f"Error during context extraction: {e}")

    return contexts

# --- Main function ---
def main():
    geckodriver_autoinstaller.install()
    driver = webdriver.Firefox()
    wait = WebDriverWait(driver, 30)
    original_window = driver.current_window_handle
    extracted_data = []
    search_phrase = "به شماره ملی"
    filter_word = "سمت"
    start_words_list = ["آقای", "خانم"] # Define the start words
    # Position mapping
    position_map = {
        "رئیس هیئت مدیره": "chairman", # More specific first
        "رئیس هیات مدیره": "chairman", # Alternate spelling
        "رئیس هیئت": "chairman",       # Shorter version
        "نایب رئیس هیئت مدیره": "viceChairman", # More specific vice chairman
        "نایب رئیس هیات مدیره": "viceChairman", # Alt spelling
        "نایب رئیس": "viceChairman",   # Added mapping
        "مدیر عامل": "ceo",            # Check after chairman
        "مدیرعامل": "ceo",            # No space
        "عضو هیئت مدیره": "boardmember",
        "عضو هیات مدیره": "boardmember",
        "عضو اصلی هیئت مدیره": "boardmember",
        "عضو علی البدل هیئت مدیره": "boardmember_alternate", # Might need separate category
        "عضو هیئت": "boardmember",    # Shorter version
        "عضو": "boardmember",          # General member (check last for board)
        "بازرس اصلی": "mainInspector",
        "بازرس علی البدل": "alternativeInspector", # Changed from supportingInspector
        "بازرس علی": "alternativeInspector" # Added and mapped
    }
    position_keywords = list(position_map.keys()) # Order matters if checking sequentially

    try:
        target_url = "https://rrk.ir/ords/r/rrs/rrs-front/%D8%AF%D8%A7%D8%AF%D9%87-%D8%A8%D8%A7%D8%B2"
        print(f"Opening {target_url}...")
        driver.get(target_url)
        print("Page opened. Waiting for elements...")

        print("Waiting for input field P199_FOOTER...")
        input_box = wait.until(EC.presence_of_element_located((By.ID, "P199_FOOTER")))
        print("Sending keys to input field...")
        input_box.send_keys("نفت")

        print("Waiting for button B912476867105247978...")
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "B912476867105247978")))
        print("Clicking button...")
        search_button.click()
        print("Search performed. Waiting for results...")

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr a[href]")))
        print("Results likely loaded. Finding result elements...")

        result_trs = driver.find_elements(By.TAG_NAME, "tr")
        print(f"Found {len(result_trs)} potential result tr elements.")

        link_urls_to_process = []
        for index, tr in enumerate(result_trs):
            try:
                link_element = tr.find_element(By.TAG_NAME, "a")
                link_url = link_element.get_attribute('href')
                if link_url and link_url.startswith('http'):
                    link_urls_to_process.append((index, link_url))
            except NoSuchElementException:
                pass

        print(f"Found {len(link_urls_to_process)} links to process.")

        # Process ALL found links
        for index, link_url in link_urls_to_process:
            print(f"\nProcessing link from row {index}: {link_url}")
            company_name = None # Initialize metadata vars
            reg_number = None
            nat_id_display = None # Changed variable name
            try:
                driver.execute_script(f"window.open('{link_url}', '_blank');")
                wait.until(EC.number_of_windows_to_be(len(driver.window_handles)))
                all_windows = driver.window_handles
                new_window = all_windows[-1]
                driver.switch_to.window(new_window)
                current_url = driver.current_url
                print(f"  Switched to new tab: {current_url}")

                # Wait for body tag
                body_locator = (By.TAG_NAME, "body")
                print("  Waiting for body tag to be present...")
                body_element = wait.until(EC.presence_of_element_located(body_locator))
                print("  Body tag found.")
                time.sleep(1) # Small delay

                # --- Extract Metadata --- 
                print("  Extracting metadata...")
                try:
                    company_input = driver.find_element(By.ID, "P28_COMPANYNAME")
                    company_name = company_input.get_attribute('value')
                    print(f"    Company Name: {company_name}")
                except NoSuchElementException:
                    print("    Company Name input (P28_COMPANYNAME) not found.")
                try:
                    reg_num_span = driver.find_element(By.ID, "P28_SABTNUMBER_DISPLAY")
                    reg_number = reg_num_span.text
                    print(f"    Reg Number: {reg_number}")
                except NoSuchElementException:
                    print("    Reg Number span (P28_SABTNUMBER_DISPLAY) not found.")
                try:
                    # Corrected ID for National ID display
                    nat_id_display_element = driver.find_element(By.ID, "P28_SABTNATIONALID_DISPLAY")
                    nat_id_display = nat_id_display_element.text
                    print(f"    Nat ID Display: {nat_id_display}")
                except NoSuchElementException:
                    print("    Nat ID Display (P28_SABTNATIONALID_DISPLAY) not found.")
                # --- End Metadata Extraction --- 

                # Get innerHTML from BODY, clean it, and extract contexts
                print("  Re-finding body and getting innerHTML...")
                # Re-find body just in case metadata extraction caused delay/change
                body_element = driver.find_element(By.TAG_NAME, "body") 
                inner_html = body_element.get_attribute('innerHTML')
                cleaned_text = remove_tags(inner_html)

                print(f"  Extracting all contexts for '{search_phrase}' starting from '{start_words_list}' ...")
                all_contexts = extract_all_phrase_contexts(cleaned_text, search_phrase, start_words=start_words_list, words_after=5)

                # Filter, Validate, Extract Position, and Save
                if all_contexts:
                    print(f"  Found {len(all_contexts)} potential context(s). Validating and extracting position...")
                    for context in all_contexts:
                        # 1. Filter by 'سمت'
                        if filter_word not in context:
                            print(f"    Skipping context (missing '{filter_word}'): '{context[:100]}...'")
                            continue
                        
                        # 2. Validate National ID (exactly one 10-digit number)
                        national_ids_found = re.findall(r'\b(\d{10})\b', context)
                        if len(national_ids_found) != 1:
                            print(f"    Skipping context (found {len(national_ids_found)} national IDs, expected 1): '{context[:100]}...'")
                            continue
                        national_id = national_ids_found[0] # Extract the ID

                        # 3. Determine Position
                        position = "unknown" # Default
                        # Iterate through keywords in order of priority (most specific first)
                        for keyword in position_keywords: 
                            if keyword in context: 
                                position = position_map[keyword]
                                print(f"    Found position keyword '{keyword}', mapped to: {position}")
                                break # Stop after finding the first matching keyword
                        if position == "unknown":
                             print(f"    No position keyword found in context: '{context[:100]}...'")

                        # 4. Add to extracted data (including context and company Nat ID display)
                        print(f"    Adding valid instance: NatID={national_id}, Pos={position}")
                        extracted_data.append({
                            "company_name": company_name,
                            "reg_number": reg_number,
                            "nat_id_display": nat_id_display, # Added back company Nat ID
                            "national_id": national_id, # Person Nat ID from context
                            "position": position,
                            "context": context # Added back the context string
                        })
                else:
                    print("  Phrase NOT found in cleaned body text by extraction function.")

            except TimeoutException:
                print("  Timed out waiting for new tab content (body tag).")
            except Exception as e:
                print(f"  Error processing tab {link_url}: {e}")
            finally:
                if len(driver.window_handles) > 1:
                    print("  Closing tab...")
                    driver.close()
                    driver.switch_to.window(original_window)
                    print("  Switched back to original tab.")
                else:
                    print("  Warning: Only one window handle found, cannot close tab.")

        print(f"\nFinished processing links.")

        if extracted_data:
            filename = "extracted_data.json"
            print(f"Saving {len(extracted_data)} entries to {filename}...")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(extracted_data, f, ensure_ascii=False, indent=4)
            print("Data saved successfully.")
        else:
            print(f"No valid data (containing phrase '{search_phrase}', filter word '{filter_word}', and exactly one National ID) was extracted.")

    except TimeoutException:
        print("Timed out waiting for page elements (initial load or results might not have loaded or locators are incorrect).")
    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        print("Quitting WebDriver...")
        driver.quit()

if __name__ == "__main__":
    main()