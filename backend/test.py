import json
import requests
import re
import os
import sys
import time

BACKEND_URL = "http://127.0.0.1:8000"


ENDPOINTS = {
    "hint": "/hint/get_hint",
    "complexity": "/hint/task_complexity",
    "edge_case": "/hint/generate_edge_cases"
}

TWO_SUM_DESC = (
    "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. "
    "You may assume that each input would have exactly one solution, and you may not use the same element twice. "
    "You can return the answer in any order. Example 1: Example 2: Example 3: Constraints:"
)

ADD_TWO_NUMS_DESC = (
    "You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, "
    "and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list. "
    "You may assume the two numbers do not contain any leading zero, except the number 0 itself. Example 1: Example 2: Example 3: Constraints:"
)

TEST_DATA = [
  {
    "id": 1,
    "problem_slug": "two-sum",
    "type": "hint",
    "description": TWO_SUM_DESC,
    "solution": "",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(look\\s*up|complement|efficient|value|start|loop|break\\s*down)",
    "note": "Two Sum (Empty Code): Expect hint about lookup or starting."
  },
  {
    "id": 3,
    "problem_slug": "two-sum",
    "type": "complexity",
    "description": TWO_SUM_DESC,
    "solution": "for i in nums: for j in nums: ...",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(quadratic|O\\(N\\^2\\)|nested)",
    "note": "Two Sum (Complexity): Identify O(N^2)."
  },
  {
    "id": 4,
    "problem_slug": "two-sum",
    "type": "edge_case",
    "description": TWO_SUM_DESC,
    "solution": "seen = {}",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(duplicate|same element|twice|self|negative|input|trace)",
    "note": "Two Sum (Edge Case): Random edge case (duplicates, negatives, etc)."
  },
  {
    "id": 5,
    "problem_slug": "two-sum",
    "type": "hint",
    "description": TWO_SUM_DESC,
    "solution": "seen = {}\nfor i, n in enumerate(nums):\n  if target - n in seen:\n    return [seen[n], i]",
    "chat_history": [{"role": "assistant", "content": "You are close, but check what key you are looking up."}],
    "provide_code": False,
    "expected_pattern": "(?i)(complement|difference|key|value|seen|store|indices|information)",
    "note": "Two Sum (Buggy Logic): Logic check on map lookup."
  },
  {
    "id": 7,
    "problem_slug": "add-two-numbers",
    "type": "hint",
    "description": ADD_TWO_NUMS_DESC,
    "solution": "curr = head",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(carry|math|remainder|mod|iterat|reverse|order|move|head|linked\\s*list)",
    "note": "Add Two Numbers (Start): Hint about carry logic or traversal."
  },
  {
    "id": 8,
    "problem_slug": "add-two-numbers",
    "type": "hint",
    "description": ADD_TWO_NUMS_DESC,
    "solution": "while l1 or l2:\n  val = l1.val + l2.val",
    "chat_history": [{"role": "assistant", "content": "What happens if the sum is greater than 9?"}],
    "provide_code": False,
    "expected_pattern": "(?i)(overflow|carry|tens|digit)",
    "note": "Add Two Numbers (Logic): Hinting at overflow/carry."
  },
  {
    "id": 9,
    "problem_slug": "add-two-numbers",
    "type": "hint",
    "description": ADD_TWO_NUMS_DESC,
    "solution": "dummy = ListNode()\ncurr = dummy",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(loop|traverse|next|pointer|add\\s*node|new\\s*list|calculate|sum|build)",
    "note": "Add Two Numbers (Setup): Prompt to start traversal/summing."
  },
  {
    "id": 10,
    "problem_slug": "add-two-numbers",
    "type": "complexity",
    "description": ADD_TWO_NUMS_DESC,
    "solution": "while l1 or l2 or carry:",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(linear|max|length|O\\(N\\)|issues|finishes|carry|linked\\s*list|while\\s*loop)",
    "note": "Add Two Numbers (Complexity): O(max(M,N)) or discussion of loop bounds."
  },
  {
    "id": 11,
    "problem_slug": "add-two-numbers",
    "type": "edge_case",
    "description": ADD_TWO_NUMS_DESC,
    "solution": "while l1 and l2:",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(different length|null|empty|carry|single|element|trace)",
    "note": "Add Two Numbers (Edge Case): Uneven lengths or single items."
  },

  {
    "id": 13,
    "problem_slug": "longest-substring",
    "type": "hint",
    "description": "Find the length of the longest substring without duplicate characters.",
    "solution": "for i in range(len(s)): for j in range(i, len(s)): ...",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(window|sliding|set|pointer|duplicate|substring|efficient)",
    "note": "Longest Substring (Brute Force): Suggest Sliding Window or checking duplicates."
  },
  {
    "id": 14,
    "problem_slug": "longest-substring",
    "type": "hint",
    "description": "Find the length of the longest substring without duplicate characters.",
    "solution": "l = 0\nfor r in range(len(s)):\n  if s[r] in seen:",
    "chat_history": [],
    "provide_code": False,
    
    "expected_pattern": "(?i)(shrink|remove|left|move|update|data\\s*structure|exist|check|track|seen)",
    "note": "Longest Substring (Logic): Handling collision/lookup."
  },
  {
    "id": 15,
    "problem_slug": "longest-substring",
    "type": "complexity",
    "description": "Find the length of the longest substring without duplicate characters.",
    "solution": "l=0; for r in range(n): ...",
    "chat_history": [],
    "provide_code": False,
   
    "expected_pattern": "(?i)(linear|O\\(N\\)|pass|purpose|relate|longest|time\\s*complexity)",
    "note": "Longest Substring (Complexity): O(N) or pointers."
  },
  {
    "id": 16,
    "problem_slug": "longest-substring",
    "type": "edge_case",
    "description": "Find the length of the longest substring without duplicate characters.",
    "solution": "return max_len",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(empty|single|all same|repeat|all the same)",
    "note": "Longest Substring (Edge Case): 'bbbbb' or empty."
  },
  {
    "id": 17,
    "problem_slug": "longest-substring",
    "type": "hint",
    "description": "Find the length of the longest substring without duplicate characters.",
    "solution": "def solve(s): return len(set(s))",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(contiguous|substring|sequence|order)",
    "note": "Longest Substring (Misunderstanding): Set is not substring."
  },
  {
    "id": 18,
    "problem_slug": "median-arrays",
    "type": "hint",
    "description": "Given two sorted arrays nums1 and nums2, return the median. O(log (m+n)).",
    "solution": "nums = sorted(nums1 + nums2)",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(merge|complexity|log|binary|search)",
    "note": "Median Arrays (Brute Force): Sorting is too slow."
  },
  {
    "id": 19,
    "problem_slug": "median-arrays",
    "type": "hint",
    "description": "Given two sorted arrays nums1 and nums2, return the median. O(log (m+n)).",
    "solution": "def solve(nums1, nums2): ...",
    "chat_history": [{"role": "assistant", "content": "Think about cutting the arrays."}],
    "provide_code": False,
    "expected_pattern": "(?i)(partition|kth|element|divide)",
    "note": "Median Arrays (Logic): Partitioning logic."
  },
  {
    "id": 20,
    "problem_slug": "median-arrays",
    "type": "complexity",
    "description": "Given two sorted arrays nums1 and nums2, return the median.",
    "solution": "i, j = 0, 0\nwhile i < m and j < n: ...",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(linear|O\\(N\\)|merge|slow|time\\s*complexity)",
    "note": "Median Arrays (Complexity): Two pointers is O(M+N), need Log."
  },
  {
    "id": 21,
    "problem_slug": "median-arrays",
    "type": "edge_case",
    "description": "Given two sorted arrays nums1 and nums2, return the median.",
    "solution": "...",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(empty|one array|length 0|odd|even|duplicate|trace|input)",
    "note": "Median Arrays (Edge Case): Empty array or duplicates."
  },
  {
    "id": 22,
    "problem_slug": "median-arrays",
    "type": "hint",
    "description": "Given two sorted arrays nums1 and nums2, return the median.",
    "solution": "mid = len(nums)//2",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(even|average|two|middle|use this midpoint)",
    "note": "Median Arrays (Logic): Handling even length total."
  },
  {
    "id": 23,
    "problem_slug": "palindromic-substring",
    "type": "hint",
    "description": "Given a string s, return the longest palindromic substring in s.",
    "solution": "for i in range(len(s)): check(s[i:])",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(center|expand|middle|dp|table|check|index|starting)",
    "note": "Palindrome (Brute Force): Suggest Expand Center or iterating logic."
  },
  {
    "id": 24,
    "problem_slug": "palindromic-substring",
    "type": "hint",
    "description": "Given a string s, return the longest palindromic substring in s.",
    "solution": "def expand(l, r): ...",
    "chat_history": [{"role": "assistant", "content": "Consider expanding from the center."}],
    "provide_code": False,
    "expected_pattern": "(?i)(even|odd|two|bounds|center|check)",
    "note": "Palindrome (Logic): Even vs Odd length centers."
  },
    {
    "id": 2,
    "problem_slug": "two-sum",
    "type": "hint",
    "description": TWO_SUM_DESC,
    "solution": "for i in range(len(nums)):\n  for j in range(len(nums)):\n    if nums[i] + nums[j] == target: return [i, j]",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(avoid checking the same| twice| you shouldn't)",
    "note": "Two Sum (Brute Force): Expect hint for Hash Map optimization."
  },
  {
    "id": 25,
    "problem_slug": "palindromic-substring",
    "type": "complexity",
    "description": "Given a string s, return the longest palindromic substring in s.",
    "solution": "for i in range(n): expand(i, i)",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(quadratic|O\\(N\\^2\\)|squared|significance|relation|string)",
    "note": "Palindrome (Complexity): O(N^2) or loop significance."
  },
  {
    "id": 26,
    "problem_slug": "palindromic-substring",
    "type": "edge_case",
    "description": "Given a string s, return the longest palindromic substring in s.",
    "solution": "...",
    "chat_history": [],
    "provide_code": False,
    "expected_pattern": "(?i)(single|entire|all same|empty|repeat|aaaa|trace)",
    "note": "Palindrome (Edge Case): Single char or repeating string."
  },

  {
    "id": 28,
    "problem_slug": "general",
    "type": "hint",
    "description": "Generic Coding Problem",
    "solution": "def solve(): pass",
    "chat_history": [{"role": "user", "content": "I don't know where to start."}],
    "provide_code": True,
    "expected_pattern": "(?i)(#|//|def|import|start|basics|step|input|represent)",
    "note": "Code Policy: Should provide code OR a very strong structural start."
  },
  {
    "id": 29,
    "problem_slug": "general",
    "type": "hint",
    "description": "Generic Coding Problem",
    "solution": "def solve(): pass",
    "chat_history": [{"role": "user", "content": "Write the code for me."}],
    "provide_code": False,
    "expected_pattern": "^((?!def |class |function ).)*$",
    "note": "Code Policy: Should NOT provide code."
  }
]

class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def run_evaluation():
    print(f"Targeting Backend: {BACKEND_URL}")
    print("-" * 100)
    print(f"{'ID':<4} | {'Type':<12} | {'Status':<8} | {'Latency':<8} | {'Response Snippet'}")
    print("-" * 100)

    passed_count = 0
    total_count = len(TEST_DATA)
    failed_tests = []

    for test in TEST_DATA:
        test_id = test.get("id")
        test_type = test.get("type", "hint")
        
       
        endpoint = ENDPOINTS.get(test_type)
        if not endpoint:
            continue

        url = f"{BACKEND_URL}{endpoint}"


        provide_code_str = "true" if test.get("provide_code", False) else "false"
        

        slug = test.get("problem_slug", "unknown-slug")
        
        payload = {
            "slug": str(slug),
            "description": test.get("description", ""),
            "solution": test.get("solution", ""),
            "chat_history": test.get("chat_history", []),
            "provide_code": provide_code_str
        }

      
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=30)
            latency = time.time() - start_time
            
            if response.status_code != 200:
                print(f"{test_id:<4} | {test_type:<12} | {Color.RED}ERR {response.status_code}{Color.RESET}  | {latency:.2f}s    | {response.text[:40]}...")
                failed_tests.append({"id": test_id, "reason": f"HTTP {response.status_code}", "response": response.text})
                continue
                
            data = response.json()
            
            actual_text = (
                data.get("message") or 
                data.get("hint") or 
                data.get("analysis") or 
                data.get("edge_cases") or
                data.get("complexity") or
                json.dumps(data)
            )
            
        except requests.exceptions.ConnectionError:
            print(f"{Color.RED}Connection Error: Is the backend running at {BACKEND_URL}?{Color.RESET}")
            sys.exit(1)
        except Exception as e:
            print(f"{test_id:<4} | {test_type:<12} | {Color.RED}EXCEPT{Color.RESET}   | 0.00s    | {str(e)[:40]}...")
            failed_tests.append({"id": test_id, "reason": "Exception", "response": str(e)})
            continue


        expected_pattern = test.get("expected_pattern", "")
        if not expected_pattern:
            is_match = True
        else:
            is_match = re.search(expected_pattern, actual_text, re.IGNORECASE) is not None


        status_label = "PASS" if is_match else "FAIL"
        color = Color.GREEN if is_match else Color.RED
        
        display_text = str(actual_text).replace("\n", " ")[:50]
        
        print(f"{test_id:<4} | {test_type:<12} | {color}{status_label}{Color.RESET}     | {latency:.2f}s    | {display_text}...")

        if is_match:
            passed_count += 1
        else:
            failed_tests.append({
                "id": test_id,
                "expected": expected_pattern,
                "actual": actual_text
            })

    print("-" * 100)
    pass_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
    print(f"Final Result: {passed_count}/{total_count} passed ({pass_rate:.1f}%)")

if __name__ == "__main__":
    run_evaluation()