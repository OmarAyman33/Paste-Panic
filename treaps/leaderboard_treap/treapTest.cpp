#include <iostream>
#include <cstdlib>
#include <ctime>
#include <algorithm>
#include <tuple>
#include <functional> // For std::function

// Including the user's assumed header file
#include "treap.h" 

using namespace std;

// The test code relies on the Treap class definition (treap<dataType>) 
// and its nested Node class (treap<dataType>::Node) being available via "treap.h".

void runTreapTest() {
    cout << "--- Treap Basic Functionality Test ---" << endl;

    // We rely on the treap class being defined in treap.h
    treap<int> myTreap;

    // --- 1. Insertion Test ---
    cout << "Expected Inorder (after 5, 2, 8, 1, 4, 9, 7): 1 2 4 5 7 8 9 (with priorities)" << endl;

    myTreap.insert(5);
    myTreap.insert(2);
    myTreap.insert(8);
    myTreap.insert(1);
    myTreap.insert(4);
    myTreap.insert(9);
    myTreap.insert(7);

    cout << "Actual Inorder: ";
    myTreap.inorder(); // Calls the public inorder()
    cout << "Treap is not empty: " << (myTreap.isEmpty() ? "False" : "True") << endl;

    // --- 2. Search Test ---
    cout << "\n--- Search Test ---" << endl;
    cout << "Search for 4: " << (myTreap.search(4) ? "Found (Expected: Found)" : "Not Found (Expected: Not Found)") << endl;
    cout << "Search for 6: " << (myTreap.search(6) ? "Found (Expected: Not Found)" : "Not Found (Expected: Not Found)") << endl;

    // --- 3. Deletion Test (Erase 5) ---
    cout << "\n--- Deletion Test (Erase 5) ---" << endl;
    myTreap.erase(5); // Calls the public erase(dataType key)
    cout << "Expected Inorder (after erasing 5): 1 2 4 7 8 9" << endl;
    cout << "Actual Inorder: ";
    myTreap.inorder();
    cout << "Search for 5: " << (myTreap.search(5) ? "Found (Expected: Not Found)" : "Not Found (Expected: Not Found)") << endl;

    // --- 4. Deletion Test (Erase 1) ---
    cout << "\n--- Deletion Test (Erase 1) ---" << endl;
    myTreap.erase(1);
    cout << "Expected Inorder (after erasing 1): 2 4 7 8 9" << endl;
    cout << "Actual Inorder: ";
    myTreap.inorder();

    // --- 5. Range Query Test (Query for [4, 8]) ---
    cout << "\n--- Range Query Test (Query for [4, 8]) ---" << endl;
    // The rangeQuery function returns a Node* to the root of the resulting treap segment.
    typename treap<int>::Node* rangeResultRoot = myTreap.rangeQuery(4, 8);

    cout << "Expected range [4, 8] content: 4 7 8" << endl;
    cout << "Actual Range Query Result: ";

    // Helper function to print the returned Node*
    // Note: typename is required when using a dependent type like Node within a template scope.
    function<void(typename treap<int>::Node*)> printNodes =
        [&](typename treap<int>::Node* node) {
        if (node) {
            printNodes(node->left);
            cout << node->key << " ";
            printNodes(node->right);
        }
        };
    printNodes(rangeResultRoot);
    cout << endl;

    // Clean up the memory for the range query result by transferring the raw pointer 
    // to a temporary treap instance whose destructor will handle deletion.
    treap<int> tempTreap;
    tempTreap.root = rangeResultRoot; // Accessing public root

    // --- 6. Copy Constructor Test ---
    cout << "\n--- Copy Constructor Test ---" << endl;
    treap<int> copiedTreap = myTreap; // Calls copy constructor
    cout << "Original Treap Inorder: ";
    myTreap.inorder();
    cout << "Copied Treap Inorder:   ";
    copiedTreap.inorder();

    // Modify the copy to ensure deep copy
    copiedTreap.insert(100);
    cout << "\nAfter inserting 100 into the COPY (only the copy should change):" << endl;
    cout << "Original Treap Inorder: ";
    myTreap.inorder();
    cout << "Copied Treap Inorder:   ";
    copiedTreap.inorder();

    cout << "\n--- Test Complete ---" << endl;
}

int main() {
    runTreapTest();
    return 0;
}