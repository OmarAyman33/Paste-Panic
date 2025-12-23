#pragma once
#include <iostream>
#include <cstdlib>
#include <stdexcept>


template<typename T>
class ImplicitTreap {

private:

	class node {
		public:
			long long priority;
			node* right;
			node* left;
			long long size;
			T value;

			node(T v) : value(v), priority(rand()), size(1),
				left(nullptr), right(nullptr) {
			}
	};

	typedef node* nodePtr;
	nodePtr root;

	//O(N) print
	void inOrderTraversal(nodePtr root) {
		if (!root) return;
		inOrderTraversal(root->left);
		std::cout << root->value << " ";
		inOrderTraversal(root->right);
	}

	void update(nodePtr t) {
		if (!t) return;
		t->size = 1 +
			(t->left ? t->left->size : 0) +
			(t->right ? t->right->size : 0);
	}

    nodePtr copySubtree(nodePtr node) {
		if (!node) return nullptr;
		nodePtr newNode = new node(node->value);
		newNode->priority = node->priority;
		newNode->size = node->size;
		newNode->left = copySubtree(node->left);
		newNode->right = copySubtree(node->right);
		return newNode;
	}

	void clear(nodePtr node) {
		if (!node) return;
		clear(node->left);   
		clear(node->right);  
		delete node;         
	}
	
	T search(nodePtr root, int k) {
		if (!root || k > (root->size) - 1 || k < 0) {
			throw std::out_of_range("index out of range");
		}
		long long num = root->left ? root->left->size : 0;
		if (k == num) return (root->value);
		else if (k < num) return search(root->left, k);
		else return search(root->right, k - num - 1);
	}

	void split(nodePtr root, long long k, nodePtr& l, nodePtr& r) {

		if (root == 0) {
			r = l = nullptr;
			return;
		}

		long long leftSize = (root->left ? root->left->size : 0);

		if (leftSize >= k) {
			split(root->left, k, l, root->left);
			r = root;

		}

		else {
			split(root->right, (k - ((leftSize)+1)), root->right, r);
			l = root;
		}
		update(root);
	}

	void merge(nodePtr& res, nodePtr l, nodePtr r) {
		if (r == 0) {
			res = l;
			return;
		}
		if (l == 0) {
			res = r;
			return;
		}
		if (r->priority >= l->priority) {

			merge(r->left, l, r->left);
			res = r;
			update(res);
		}
		else {

			merge(l->right, l->right, r);
			res = l;
			update(res);
		}

	}

public:

	ImplicitTreap() : root(nullptr) {}
	ImplicitTreap(T v) : root(new node(v)) {}
	ImplicitTreap(const ImplicitTreap& T) : root(copySubtree(T.root)){}



	~ImplicitTreap() {
		clear(root);
	}

	long long size() const { return root ? root->size : 0; }


	void print() {
		inOrderTraversal(root);
		std::cout << endl;
	}

	void insert(long long pos, T val) {
		if (pos < 0 || pos > size()) {
			std::cerr << "Insert position out of range";
			return;
		}
		nodePtr L, R;
		split(root, pos, L, R);

		nodePtr N = new node(val);

		merge(L, L, N);
		merge(root, L, R);
	}

	void paste(long long pos, ImplicitTreap& t) {
		if (pos < 0 || pos > size()) {
			std::cerr << "Insert position out of range";
			return;
		}
		nodePtr L, R;
		split(root, pos, L, R);

		nodePtr N = copySubtree(t.root);

		merge(L, L, N);
		merge(root, L, R);
	}
	
	void erase(long long pos) {
		if (pos < 0 || pos >= size()) {
			std::cerr << "Erase position out of range";
			return;
		}
		nodePtr L, R, mid;
		split(root, pos, L, R);       // the right treap starts with the position that i want to erase
		split(R, 1, mid, R);
		clear(mid);
		merge(root,L, R);
	}

	//erase a region
	void slit(long long ipos, long long fpos) {
		if (ipos < 0 || fpos > size() || ipos >= fpos) {
			std::cerr << "Invalid range for erase";
			return;
		}
		nodePtr L, R, mid;
		split(root, ipos, L, R);       // the right treap starts with the position that i want to erase
		split(R, fpos-ipos, mid, R);
		clear(mid);
		merge(root, L, R);
	}

	//ipos is initial position in the selected region included.
	//fpos is final position in the selected region excluded (yes this makes it easier for me)
	Treap copy(long long ipos, long long fpos){

		if (ipos < 0 || fpos > size() || ipos >= fpos) {
			std::cerr << "Invalid range for copy";
			return Treap();
		}
		nodePtr first = nullptr, second = nullptr, third = nullptr;
		split(root, ipos, first, second);
		split(second, fpos - ipos, second, third);

		Treap result;
		result.root = copySubtree(second);

		nodePtr temp = nullptr;
		merge(temp, first, second);
		merge(root, temp, third);

		return result;
	}

	Treap cut(long long ipos, long long fpos){

		if (ipos < 0 || fpos > size() || ipos >= fpos) {
			std::cerr << "Invalid range for copy";
			return Treap();
		}
		nodePtr first = nullptr, second = nullptr, third = nullptr;
		split(root, ipos, first, second);
		split(second, fpos - ipos, second, third);

		Treap result;
		result.root = second;

		merge(root, first, third);

		return result;
	}

	void delete_range(long long ipos, long long fpos){
		Treap var = cut(ipos, fpos);
	}
	
	T search(long long k) {
		if (!root) {
			throw std::out_of_range("empty Treap");
		}
		return search(root, k);
	}

	Treap& operator=(const Treap& other) {
		if (this != &other) {
			clear(root);
			root = copySubtree(other.root);
		}
		return *this;
	}
};

