from typing import List, Dict, Any, Union


def insertion_sort_by_field(students: List[Dict[str, Any]], field: str) -> List[Dict[str, Any]]:
    """
    Sorts a list of student dicts in place ascending by the given field ('age' or 'name').
    Hand-written Insertion Sort using an outer loop and inner while shifting loop.
    NO built-in sorted() or list.sort() calls inside.
    """
    n = len(students)
    for i in range(1, n):
        key_item = students[i]
        key_val = key_item[field]
        j = i - 1
        
        # Shift elements of students[0..i-1] that are greater than key_val to one position ahead
        while j >= 0 and students[j][field] > key_val:
            students[j + 1] = students[j]
            j -= 1
            
        students[j + 1] = key_item
        
    return students


def binary_search_by_name(sorted_by_name_list: List[Dict[str, Any]], name: str) -> Union[Dict[str, Any], int]:
    """
    Hand-written iterative Binary Search on a list sorted alphabetically by name.
    Uses overflow-safe midpoint formula mid = low + (high - low) // 2.
    Returns matching student dict if found, or -1 if not found.
    """
    low = 0
    high = len(sorted_by_name_list) - 1
    
    target_name = name.strip().lower()
    
    while low <= high:
        mid = low + (high - low) // 2
        mid_name = sorted_by_name_list[mid]["name"].strip().lower()
        
        if mid_name == target_name:
            return sorted_by_name_list[mid]
        elif mid_name < target_name:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1


def format_roster_report(students: List[Dict[str, Any]]) -> str:
    """
    Returns a multi-line string built with f-strings, one line per student:
    "[Age {age}] {name} <{email}>"
    """
    lines = []
    for s in students:
        lines.append(f"[Age {s['age']}] {s['name']} <{s['email']}>")
    return "\n".join(lines)


def count_students_meeting_min_age(students: List[Dict[str, Any]], min_age: int) -> int:
    """
    Counts how many students have age >= min_age using an explicit loop with an accumulator variable.
    """
    count = 0
    for student in students:
        if student.get("age", 0) >= min_age:
            count += 1
    return count
