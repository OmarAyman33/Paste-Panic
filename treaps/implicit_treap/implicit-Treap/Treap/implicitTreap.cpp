#pragma once
#include <iostream>
#include <string>
#include <cstdlib>
#include <stdexcept>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace std;

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

    nodePtr copySubtree(nodePtr root) {
        if (!root) return nullptr;
        nodePtr newNode = new node(root->value);
        newNode->priority = root->priority;
        newNode->size = root->size;
        newNode->left = copySubtree(root->left);
        newNode->right = copySubtree(root->right);
        return newNode;
    }

    void clear(nodePtr root) {
        if (!root) return;
        clear(root->left);
        clear(root->right);
        delete root;
    }

	T _search(nodePtr root, long long k) {
		if (!root || k > (root->size) - 1 || k < 0) {
			throw std::out_of_range("index out of range");
		}
		long long num = root->left ? root->left->size : 0;
		if (k == num) return (root->value);
		else if (k < num) return _search(root->left, k);
		else return _search(root->right, k - num - 1);
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

	void insert_last(T val) {
		insert(size(), val);
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
	// void slit(long long ipos, long long fpos) {
	// 	if (ipos < 0 || fpos > size() || ipos >= fpos) {
	// 		std::cerr << "Invalid range for erase";
	// 		return;
	// 	}
	// 	nodePtr L, R, mid;
	// 	split(root, ipos, L, R);       // the right treap starts with the position that i want to erase
	// 	split(R, fpos-ipos, mid, R);
	// 	clear(mid);
	// 	merge(root, L, R);
	// }

	//ipos is initial position in the selected region included.
	//fpos is final position in the selected region excluded (yes this makes it easier for me)
	ImplicitTreap copy(long long ipos, long long fpos){

		if (ipos < 0 || fpos > size() || ipos >= fpos) {
			std::cerr << "Invalid range for copy";
			return ImplicitTreap();
		}
		nodePtr first = nullptr, second = nullptr, third = nullptr;
		split(root, ipos, first, second);
		split(second, fpos - ipos, second, third);

		ImplicitTreap result;
		result.root = copySubtree(second);

		nodePtr temp = nullptr;
		merge(temp, first, second);
		merge(root, temp, third);

		return result;
	}

	ImplicitTreap cut(long long ipos, long long fpos){

		if (ipos < 0 || fpos > size() || ipos >= fpos) {
			std::cerr << "Invalid range for copy";
			return ImplicitTreap();
		}
		nodePtr first = nullptr, second = nullptr, third = nullptr;
		split(root, ipos, first, second);
		split(second, fpos - ipos, second, third);

		ImplicitTreap result;
		result.root = second;

		merge(root, first, third);

		return result;
	}

	void delete_range(long long ipos, long long fpos){
		ImplicitTreap var = cut(ipos, fpos);
	}

	T search(long long k) {
		if (!root) {
			throw std::out_of_range("empty Treap");
		}
		return _search(root, k);
	}

	int check_equal_so_far(const string &other , bool& complete) {
		int n = size();
		int other_len = (int)other.length();
		for (int i = 0; i < n; i++) {
			if (search(i) != other[i]) return i;
		}
		complete = (n == other_len);
    	return -1;
	}

	ImplicitTreap& operator=(const ImplicitTreap& other) {
		if (this != &other) {
			clear(root);
			root = copySubtree(other.root);
		}
		return *this;
	}

	string to_string() {
		string result = "";
		for (long long i = 0; i < size(); i++) {
			result += search(i);
		}
		return result;
	}

};

PYBIND11_MODULE(implicit_treap, m) {
	pybind11::class_<ImplicitTreap<char>>(m, "implicittreap")
		.def(pybind11::init<>())
		.def("insert", &ImplicitTreap<char>::insert)
		.def("erase", &ImplicitTreap<char>::erase)
		.def("copy", &ImplicitTreap<char>::copy)
		.def("cut", &ImplicitTreap<char>::cut)
		.def("size", &ImplicitTreap<char>::size)
		.def("search", &ImplicitTreap<char>::search)
		.def("delete_range", &ImplicitTreap<char>::delete_range)
		.def("print", &ImplicitTreap<char>::print)
		.def("insert_last", &ImplicitTreap<char>::insert_last)
		.def("paste", &ImplicitTreap<char>::paste)
		.def("check_equal_so_far", [](ImplicitTreap<char>& self, const std::string& other) {
            bool complete = false;
            int first_error = self.check_equal_so_far(other, complete);
            return pybind11::make_tuple(first_error, complete);
        })
		.def("to_string", &ImplicitTreap<char>::to_string);
}