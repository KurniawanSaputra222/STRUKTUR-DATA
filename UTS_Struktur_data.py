import csv
import re
import textwrap
import threading
import itertools
import sys
import time
import urllib.request

def clean_text(text):
    return re.sub(r'\s+', ' ', str(text)).strip()

def loading_animation(text="Retrieving data"):
    stop_event = threading.Event()
    def spin():
        for c in itertools.cycle(['|', '/', '-', '\\']):
            if stop_event.is_set():
                break
            sys.stdout.write(f'\r{text} {c}')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(text) + 2) + '\r')
    t = threading.Thread(target=spin)
    t.start()
    return stop_event.set

def fetch_data(url):
    stop_loading = loading_animation("Loading from URL")
    try:
        with urllib.request.urlopen(url) as response:
            lines = [l.decode('utf-8') for l in response.readlines()]
            reader = csv.DictReader(lines)
            data = [{k: clean_text(row.get(k, '')) for k in reader.fieldnames} for row in reader]
        return data
    except Exception as e:
        print(f"\nFailed to read data from URL: {e}")
        return []
    finally:
        stop_loading()
        time.sleep(0.2)

def wrap(label, text):
    lines = textwrap.wrap(text.strip(), width=68)
    if not lines:
        return f"{label:<10}:"
    result = [f"{label:<10}: {lines[0]}"]
    result.extend(f"{' '*12}{l}" for l in lines[1:])
    return "\n".join(result)

def display(item):
    field_map = {
        "No": "No",
        "NIM": "NIM",
        "Name": "Nama Mahasiswa",
        "Database": "Sumber Database",
        "Topic": "Fokus Kata Kunci (Pilih No.1 atau 2 atau 3) sesuai yg ada di soal",
        "Title": "Judul Paper",
        "Year": "Tahun Terbit",
        "Author": "Nama Penulis",
        "Link": "Link Paper",
    }
    print("\n" + "="*40)
    for label, key in field_map.items():
        val = item.get(key, '')
        print(wrap(label, val) if label in ["Title", "Author"] else f"{label:<10}: {val}")
    print("="*40)

def search(data, keyword, column, binary=False):
    column_map = {1: 'Judul Paper', 2: 'Tahun Terbit', 3: 'Nama Penulis'}
    key = column_map.get(column)
    if not key:
        print("Invalid column.")
        return

    keyword = keyword.lower()
    if binary:
        data.sort(key=lambda item: item[key].lower())
        results = binary_search(data, keyword, key)
    else:
        results = [item for item in data if keyword in item[key].lower()]

    if results:
        for item in results:
            display(item)
        print(f"Found {len(results)} data.")
    else:
        print("Data not found!")

def binary_search(data, keyword, key):
    low, high = 0, len(data) - 1
    results = []
    while low <= high:
        mid = (low + high) // 2
        value = data[mid][key].lower()
        if keyword == value:
            left = mid
            while left >= 0 and data[left][key].lower() == keyword:
                left -= 1
            right = mid
            while right < len(data) and data[right][key].lower() == keyword:
                right += 1
            results = data[left + 1:right]
            break
        elif keyword < value:
            high = mid - 1
        else:
            low = mid + 1
    return results

def main():
    # Link URL Dari Google Sheet
    url = "https://docs.google.com/spreadsheets/d/17ru4XAU2NloE9Dfxr2PC1BVcsYkLLT5r7nPSsiOFlvQ/export?format=csv&gid=743838712"
    journals = fetch_data(url)
    if not journals:
        return

    while True:
        print("\nJournal Search")
        print("1. Linear Search\n2. Binary Search\n3. Exit")
        try:
            menu = int(input("Select menu: "))
            if menu == 3:
                break
            if menu not in (1, 2):
                continue
            column = int(input("\nSearch by: \n1. Judul Paper\n2. Tahun Terbit\n3. Nama Penulis\nSelect: "))
            keyword = input("Enter keyword: ")
            print("\nSearch Results:\n")
            search(journals, keyword, column, binary=(menu == 2))
        except ValueError:
            print("Invalid input!")
            
if __name__ == "__main__":
    main()