from typing import List, Dict, Any, Union, Tuple


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
        
        while j >= 0 and students[j][field] > key_val:
            students[j + 1] = students[j]
            j -= 1
            
        students[j + 1] = key_item
        
    return students


def insertion_sort_by_field_with_metrics(students: List[Dict[str, Any]], field: str) -> Tuple[List[Dict[str, Any]], int, int]:
    """
    Hand-written Insertion Sort returning (sorted_list, comparisons_count, shifts_count).
    """
    n = len(students)
    comparisons = 0
    shifts = 0
    
    for i in range(1, n):
        key_item = students[i]
        key_val = key_item[field]
        j = i - 1
        
        while j >= 0:
            comparisons += 1
            if students[j][field] > key_val:
                students[j + 1] = students[j]
                shifts += 1
                j -= 1
            else:
                break
                
        students[j + 1] = key_item
        
    return students, comparisons, shifts


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


def binary_search_by_name_with_trace(sorted_by_name_list: List[Dict[str, Any]], name: str) -> Tuple[Union[Dict[str, Any], int], int, List[Dict[str, Any]]]:
    """
    Hand-written iterative Binary Search returning (result, iteration_count, execution_trace).
    """
    low = 0
    high = len(sorted_by_name_list) - 1
    target_name = name.strip().lower()
    iterations = 0
    trace = []
    
    while low <= high:
        iterations += 1
        mid = low + (high - low) // 2
        mid_name = sorted_by_name_list[mid]["name"].strip().lower()
        
        step_info = {
            "step": iterations,
            "low": low,
            "high": high,
            "mid": mid,
            "mid_student_name": sorted_by_name_list[mid]["name"]
        }
        trace.append(step_info)
        
        if mid_name == target_name:
            return sorted_by_name_list[mid], iterations, trace
        elif mid_name < target_name:
            low = mid + 1
        else:
            high = mid - 1
            
    return -1, iterations, trace


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
