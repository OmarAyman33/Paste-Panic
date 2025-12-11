#pragma once
#include<random>
#include<tuple>
#include<iostream>
using namespace std;
// I'm placing the implementations in the .h file because C++'s compilation differs with template functions, making it difficult
// for the implementation of template functions in seperate .cpp files. another solution is using .tpp files though frankly,
// I havent done much research about it.
template<class dataType>
class treap
{
public:
	class Node { // made the node class public because gemini couldnt comprehend that it was private when generating test cases
	public:
		dataType key;
		int priority;
		Node* left, * right;
		inline Node(dataType k) {
			this->key = k;
			left = right = nullptr;
			priority = rand();
		}
	};
private:
	Node* rightRotate(Node* root);
	Node* leftRotate(Node* root);
	Node* copyTree(Node* node);
	void inorder(Node* node);
	Node* merge(Node* a, Node* b);
public:
	Node* insert(Node* root, dataType key, int priority);
	Node* root;
	treap();
	treap(const treap& other); // copy constructor
	void insert(dataType key);
	Node* insert(Node* root, dataType key);
	Node* erase(Node* root, dataType key);
	bool search(dataType key);
	void erase(dataType key);
	bool isEmpty();
	tuple<Node*, Node*> split(dataType pivot);
	Node* rangeQuery(dataType min, dataType max);
	void inorder();
	template<class dataType>
	typename treap<dataType>::Node* treap<dataType>::merge(treap<dataType>& treap1, treap<dataType>& treap2) {
		return merge(treap1.root, treap2.root);
	}
};

// constuctor
template<class dataType>
treap<dataType>::treap() {
	root = nullptr;
}
template<class dataType>


bool treap<dataType>::isEmpty() {
	if (root == nullptr)
		return true;
	return false;
}

// helper rotation functions

// right rotation
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::rightRotate(Node* root) {
	Node* newRoot = root->left;
	root->left = newRoot->right;
	newRoot->right = root;
	root = newRoot;
	return newRoot;
}

// left rotation
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::leftRotate(Node* root) {
	Node* newRoot = root->right;
	root->right = newRoot->left;
	newRoot->left = root;
	root = newRoot;
	return newRoot;
}


// recursive insert function
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::insert(Node* root, dataType key) {
	// base case, root is null, therefore node should be inserted in this position
	if (root == nullptr) {
		return new Node(key);
	}
	if (key <= root->key) {

		root->left = insert(root->left, key); // insert key in left subtree
		if (root->left->priority < root->priority)
			root = rightRotate(root);
	}
	else {
		root->right = insert(root->right, key);

		if (root->right->priority < root->priority)
			root = leftRotate(root);
	}
	return root;
}


// static/non-recursive insert functions
template<class dataType>
void treap<dataType>::insert(dataType key) {
	if (this->isEmpty()) {
		root = new Node(key);
		return;
	}
	root = insert(root, key);
}

// typical BST search function
template<class dataType>
bool treap<dataType>::search(dataType key) { 
	if (this->isEmpty()) {
		return false;
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
			return true;
	}
	return false;
}


template<class dataType>
void treap<dataType>::erase(dataType key) {
	root = erase(root, key);
}


template<class dataType>
typename treap<dataType>::Node* treap<dataType>::erase(Node* root, dataType key) {
	// base case (element not in treap)
	if (root == nullptr) return root;
	// if the key is not at the root, call the function for the corresponding subtree:
	if (key < root->key) {
		root->left = erase(root->left, key);
	}
	else if (key > root->key) {
		root->right = erase(root->right, key);
	}
	// here, we handle the logic of deleting the node.
	// if only one child subtree is present, it just takes the place of the deleted node.
	else if (root->left == nullptr) {
		Node* temp = root->right;
		delete(root);
		root = temp;
	}
	else if (root->right == nullptr) {
		Node* temp = root->left;
		delete(root);
		root = temp;
	}
	// if both subtrees are present, we need to compare their priorities and complete the corresponding rotations
	else if (root->left->priority > root->right->priority) {
		root = leftRotate(root);
		root->left = erase(root->left, key);
	}
	else {
		root = rightRotate(root);
		root->right = erase(root->right, key);
	}
	return root;
}


// insert function with manual priority for easier splitting.
template<class dataType>
typename treap<dataType>::Node* treap<dataType>::insert(Node* root, dataType key, int priority) {
	if (root == nullptr) {
		Node* newNode = new Node(key);
		newNode->priority = priority;
		return newNode;
	}
	if (key <= root->key) {
		root->left = insert(root->left, key, priority);
		if (root->left->priority < root->priority)
			root = rightRotate(root);
	}
	else {
		root->right = insert(root->right, key, priority);
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
	treap<dataType> newtreap = treap(*this);
	newtreap.root = newtreap.insert(newtreap.root, pivot, -1);
	return make_tuple(newtreap.root->left, newtreap.root->right);
}

template<class dataType>
typename treap<dataType>::Node* treap<dataType>::rangeQuery(dataType min, dataType max) {
	// this function returns a pointer to a treap which represents all the elements between min and max
	tuple<Node*, Node*> x = this->split(min);
	Node* left = get<0>(x);
	Node* right = get<1>(x);

	treap<dataType> temp;
	temp.root = right;
	tuple<Node*, Node*> y = temp.split(max);

	Node* middle = get<0>(y);

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
		return a;
	}
	else {
		b->left = merge(a, b->left);
		return b;
	}
}
