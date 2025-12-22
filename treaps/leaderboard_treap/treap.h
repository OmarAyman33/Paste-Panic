#pragma once
#include<random>
#include<tuple>
#include<iostream>
using namespace std;

template<class dataType>
class treap
{
public:
    class Node {
    public:
        dataType key;
        int priority;
        Node* left, * right;
        int subtreeSize;
        inline Node(dataType k) {
            this->key = k;
            left = right = nullptr;
            subtreeSize = 1;
            priority = rand();
        }
    };

private:
    Node* rightRotate(Node* root);
    Node* leftRotate(Node* root);
    Node* copyTree(Node* node);
    void inorder(Node* node);
    Node* merge(Node* a, Node* b);
    int getSize(Node* n);
    void updateSize(Node* n);
    Node* getK(Node* root, int k);
    dataType* convertToArray(Node* root);

    // FIX 1: Removed 'treap<dataType>::' qualifier from inside the class
    void fillArray(Node* root, dataType* arr, int& index);

public:
    Node* insert(Node* root, dataType key, int priority);
    Node* root;
    treap();
    treap(const treap& other); // copy constructor
    void insert(dataType key);
    Node* insert(Node* root, dataType key);
    Node* erase(Node* root, dataType key);
    Node* search(dataType key);
    void erase(dataType key);
    bool isEmpty();
    tuple<Node*, Node*> split(dataType pivot);
    Node* rangeQuery(dataType min, dataType max);
    void inorder();
    dataType getK(int k);
    dataType* getTopK(int k);
    void updateNode(dataType oldNode, dataType newNode);

    // FIX 2: Simplified syntax. Removed template header and scope qualifier.
    // Also, this calls the private merge(Node*, Node*).
    Node* merge(treap<dataType>& treap1, treap<dataType>& treap2) {
        return merge(treap1.root, treap2.root);
    }
};

// --- Implementations ---

template<class dataType>
treap<dataType>::treap() {
    root = nullptr;
}

template<class dataType>
bool treap<dataType>::isEmpty() {
    return root == nullptr;
}

// Right Rotation
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::rightRotate(Node* root) {
    Node* newRoot = root->left;
    root->left = newRoot->right;
    newRoot->right = root;

    updateSize(root);
    updateSize(newRoot);

    return newRoot;
}

// Left Rotation
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::leftRotate(Node* root) {
    Node* newRoot = root->right;
    root->right = newRoot->left;
    newRoot->left = root;

    updateSize(root);
    updateSize(newRoot);

    return newRoot;
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::insert(Node* root, dataType key) {
    if (root == nullptr) {
        return new Node(key);
    }
    if (key <= root->key) {
        root->left = insert(root->left, key);
        updateSize(root);
        if (root->left->priority < root->priority)
            root = rightRotate(root);
    }
    else {
        root->right = insert(root->right, key);
        updateSize(root);
        if (root->right->priority < root->priority)
            root = leftRotate(root);
    }
    return root;
}

template<class dataType>
void treap<dataType>::insert(dataType key) {
    if (this->isEmpty()) {
        root = new Node(key);
        return;
    }
    root = insert(root, key);
}

// FIX 3: Fixed return type mismatch. 'false' is bool, but function returns Node*.
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::search(dataType key) {
    if (this->isEmpty()) {
        return nullptr; // Changed from false
    }
    Node* curr = root;
    while (curr != nullptr) {
        if (key > curr->key) {
            curr = curr->right;
        }
        else if (key < curr->key) {
            curr = curr->left;
        }
        else
            return curr;
    }
    return nullptr;
}

template<class dataType>
void treap<dataType>::erase(dataType key) {
    root = erase(root, key);
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::erase(Node* root, dataType key) {
    if (root == nullptr) return root;

    if (key < root->key) {
        root->left = erase(root->left, key);
        updateSize(root);
    }
    else if (key > root->key) {
        root->right = erase(root->right, key);
        updateSize(root);
    }
    else if (root->left == nullptr) {
        Node* temp = root->right;
        delete(root);
        root = temp;
        updateSize(root);
    }
    else if (root->right == nullptr) {
        Node* temp = root->left;
        delete(root);
        root = temp;
        updateSize(root);
    }
    else if (root->left->priority > root->right->priority) {
        root = leftRotate(root);
        root->left = erase(root->left, key);
        updateSize(root);
    }
    else {
        root = rightRotate(root);
        root->right = erase(root->right, key);
        updateSize(root);
    }
    return root;
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::insert(Node* root, dataType key, int priority) {
    if (root == nullptr) {
        Node* newNode = new Node(key);
        newNode->priority = priority;
        return newNode;
    }
    if (key <= root->key) {
        root->left = insert(root->left, key, priority);
        updateSize(root);
        if (root->left->priority < root->priority)
            root = rightRotate(root);
    }
    else {
        root->right = insert(root->right, key, priority);
        updateSize(root);
        if (root->right->priority < root->priority)
            root = leftRotate(root);
    }
    return root;
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::copyTree(Node* node) {
    if (node == nullptr) return nullptr;
    Node* newNode = new Node(node->key);
    newNode->priority = node->priority;
    newNode->subtreeSize = node->subtreeSize;
    newNode->left = copyTree(node->left);
    newNode->right = copyTree(node->right);
    return newNode;
}

template<class dataType>
treap<dataType>::treap(const treap<dataType>& other) {
    root = copyTree(other.root);
}

template<class dataType>
tuple<typename treap<dataType>::Node*, typename treap<dataType>::Node*> treap<dataType>::split(dataType pivot) {
    // Note: This implementation copies the tree, splits the copy, and returns pointers to the copy.
    // Be careful with memory management here as 'newtreap' goes out of scope.
    treap<dataType> newtreap = treap(*this);
    newtreap.root = newtreap.insert(newtreap.root, pivot, -1);

    // We are deliberately leaking these pointers from the stack object 'newtreap' so they survive return.
    // Ideally, you should prevent newtreap destructor from deleting these nodes, 
    // or implement split properly without copying the whole tree class.
    Node* l = newtreap.root->left;
    Node* r = newtreap.root->right;

    // Detach so destructor doesn't kill them? 
    // This part of your logic is risky but I am leaving it as per your implementation logic.
    newtreap.root->left = nullptr;
    newtreap.root->right = nullptr;

    return make_tuple(l, r);
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::rangeQuery(dataType min, dataType max) {
    tuple<Node*, Node*> x = this->split(min);
    Node* right = get<1>(x);

    treap<dataType> temp;
    temp.root = right;
    tuple<Node*, Node*> y = temp.split(max);

    Node* middle = get<0>(y);
    // Important: Prevent temp destructor from deleting 'middle'
    // This logic needs careful memory handling but fixing compilation first.
    return middle;
}

template<class dataType>
void treap<dataType>::inorder(Node* node) {
    if (node == nullptr) return;
    inorder(node->left);
    cout << node->key << " ";
    inorder(node->right);
}

template<class dataType>
void treap<dataType>::inorder() {
    inorder(root);
    cout << endl;
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::merge(Node* a, Node* b) {
    if (a == nullptr) return b;
    if (b == nullptr) return a;

    if (a->priority < b->priority) {
        a->right = merge(a->right, b);
        updateSize(a); // Only update a, b is essentially gone/merged
        return a;
    }
    else {
        b->left = merge(a, b->left);
        updateSize(b);
        return b;
    }
}

template<class dataType>
int treap<dataType>::getSize(Node* n) {
    return n ? n->subtreeSize : 0;
}

template<class dataType>
void treap<dataType>::updateSize(Node* n) {
    if (n) {
        n->subtreeSize = 1 + getSize(n->left) + getSize(n->right);
    }
}

// FIX 4: Safety check for left child
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::getK(Node* root, int k) {
    if (!root || k > root->subtreeSize)
        return nullptr;

    int leftSize = getSize(root->left); // Safer than root->left->subtreeSize

    if (k <= leftSize)
        return getK(root->left, k);
    if (k == leftSize + 1)
        return root;

    return getK(root->right, k - leftSize - 1);
}

// FIX 5: Cannot return nullptr for a Value Type.
// If dataType is 'Leaderboard_time', you can't return NULL.
// Changed to return pointers or you must handle the 'not found' case differently.
// For now, I'm assuming you want the value, so we must assume k is valid or throw.
template<class dataType>
dataType treap<dataType>::getK(int k) {
    Node* result = getK(root, k);
    if (result)
        return result->key;
    // If not found, returning a default constructed object is the only safe option for templates
    return dataType();
}

template<class dataType>
void treap<dataType>::fillArray(Node* root, dataType* arr, int& index) {
    if (root == nullptr) return;

    fillArray(root->left, arr, index);
    arr[index] = root->key;
    index++;
    fillArray(root->right, arr, index);
}

template<class dataType>
dataType* treap<dataType>::convertToArray(Node* root) {
    if (root == nullptr) {
        return nullptr;
    }
    int size = root->subtreeSize;
    dataType* arr = new dataType[size];
    int index = 0;
    fillArray(root, arr, index);
    return arr;
}

template<class dataType>
dataType* treap<dataType>::getTopK(int k) {
    // If k is larger than tree size, return everything
    if (k >= root->subtreeSize) {
        return convertToArray(root);
    }

    // Note: Your logic here assumes rangeQuery works perfectly. 
    // Given the issues with split/copy, verify this logic carefully.
    dataType k_element = getK(k);

    Node* curr = root;
    while (curr->left != nullptr) {
        curr = curr->left;
    }
    // Getting items from Minimum to K-th element
    Node* topKTreap = rangeQuery(curr->key, k_element);
    return convertToArray(topKTreap);
}

template<class dataType>
void treap<dataType>::updateNode(dataType oldNode, dataType newNode) {
    erase(oldNode);
    insert(newNode);
}