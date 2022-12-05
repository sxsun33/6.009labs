# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences

class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree, or reassign the
        associated value if it is already present.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is not
        a string.
        """

        if not isinstance(key, str): 
            raise TypeError

        if key[0] in self.children:
            node = self.children[key[0]]
        
        else:
            node = PrefixTree()
            self.children[key[0]] = node

        if len(key) == 1:
            node.value = value
        else:
            node[key[1:]] = value  


    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the prefix tree, raise a KeyError.  If the given key is not a string,
        raise a TypeError.
        """

        if not isinstance(key, str):
            raise TypeError
        
        if key[0] in self.children:
            node = self.children[key[0]]
        
        else:
            raise KeyError

        if len(key) == 1: 
            if node.value is None:
                raise KeyError
            else:
                return node.value 

        else:
            return node[key[1:]]
        
    def get_node(self, key):
        """
        Return the node for the specified prefix. If the given key is not a string,
        raise a TypeError.
        """
        if not isinstance(key, str):
            raise TypeError
        
        if len(key) == 0:
            return self

        if key[0] in self.children:
            node = self.children[key[0]]
        
        else:
            return None

        if len(key) == 1: 
            return node 

        else:
            return node.get_node(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists. If the given
        key is not in the prefix tree, raise a KeyError.  If the given key is
        not a string, raise a TypeError.
        """
        if not isinstance(key, str):
            raise TypeError
        if key not in self:
            raise KeyError

        if key[0] in self.children:
            node = self.children[key[0]]
        
        else:
            raise KeyError

        if len(key) == 1:
            node.value = None
        else:
            del node[key[1:]]

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.  If the given
        key is not a string, raise a TypeError.
        """
        if not isinstance(key, str):
            raise TypeError
        
        if len(key) == 0:
            return False
        
        if key[0] in self.children:
            node = self.children[key[0]]
        else:
            return False

        if len(key) == 1:
            if node.value is None:
                return False
            return True

        return key[1:] in node

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        for child in self.children:
            key = child
            if self.children[child].value is not None:
                value = self.children[child].value
                yield (key, value)
                
            if self.children[child].children != {}:
                for k, val in self.children[child]:
                    yield (key + k, val)   

def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    text = tokenize_sentences(text)
    word_dict = {} # a dict mapping words to their frequencies
    for t in text:
        for word in t.split():
            if word not in word_dict:
                word_dict[word] = 1
            else:
                word_dict[word] += 1

    word_tree = PrefixTree()
    for w, f in word_dict.items():
        word_tree[w] = f
    return word_tree   

def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError

    if max_count is not None and max_count <= 0:
        return []

    subtree = tree.get_node(prefix)

    if subtree == None:
        return []

    try:
        result_list = [(prefix, tree[prefix])]
    except:
        result_list = []

    for k, val in subtree:
        result_list.append((prefix + k, val))
    result_list.sort(reverse = True, key = lambda x: x[1])

    if max_count is None or max_count > len(result_list):
        return [word for word, _ in result_list]
    else:
        return [result_list[i][0] for i in range(max_count)]

def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    autofill_list = autocomplete(tree, prefix, max_count)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    if max_count is not None and len(autofill_list) == max_count:
        return autofill_list
    autofill_set = set(autofill_list)
    def insert_char():
        result = []
        for i in range(26):
            for j in range(len(prefix) + 1):
                word = prefix[:j] + alphabet[i] + prefix[j:]
                if word in tree:
                    result.append((word, tree[word]))
        return result

    def del_char():
        result = []
        for i in range(len(prefix)):
            word = prefix[:i] + prefix[i+1:]
            if word in tree:
                result.append((word, tree[word]))
        return result
    
    def replace_char():
        result = []
        for i in range(26):
            for j in range(len(prefix) + 1):
                word = prefix[:j] + alphabet[i] + prefix[j+1:]
                if word in tree:
                    result.append((word, tree[word]))
        return result

    def transpose():
        result = []
        n = len(prefix)

        for i in range(n - 2):
            word = prefix[:i] + prefix[i + 1] + prefix[i] + prefix[i+2:]
            if word in tree:
                result.append((word, tree[word]))
        if n >= 2:
            word1 = prefix[:n - 2] + prefix[n - 1] + prefix[n - 2]
        if word1 in tree:
            result.append((word1, tree[word1]))
        return result

    full_list =  insert_char() + del_char() + replace_char() + transpose()   
    
    if max_count is None:
        return list(autofill_set | {word for word, _ in full_list})
    else:
        full_list.sort(reverse = True, key = lambda x: x[1])
        while len(autofill_list) != max_count:
            x, _ = full_list.pop(0)
            if x not in autofill_set:
                autofill_list.append(x)
                autofill_set.add(x)
        return autofill_list            

def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    n = len(pattern)
    for i in range(len(pattern)):
        if n - 2 - i >= 0:
            if pattern[n - 1 - i] == '*' and pattern[n - 2 - i] == '*':
                pattern = pattern[:n - 2 - i] + pattern[n - 1 - i:]

    def recursion_helper(result, pat):
        if len(pat) == 0:
            result_list = []
            for word in result:
                if word in tree:
                    result_list.append((word, tree[word]))
            return result_list

        else:
            def edit_new_list(node, seg, char):
                if char != '*' and char != '?':
                    if char in node.children:
                        new_list.append(seg + char)
                if char == '?':
                    for letter in node.children:
                        new_list.append(seg + letter)
                if char == '*':
                    new_list.append(seg)
                    if len(pat) == 1:
                        for frag, _ in node:
                            new_list.append(seg + frag)
                    else:
                        for frag in valid_fragments(node):
                            new_list.append(seg + frag)

            def valid_fragments(node):
                # return a generator of all valid word fragments in a node for * not at the end of the pattern

                for child, tree in node.children.items():
                    if len(tree.children) != 0:
                        yield child

                        for key in valid_fragments(tree):
                            yield (child + key)                        

            new_list = []
            char = pat[0]
            if len(result) == 0:
                node = tree
                seg = ''
                edit_new_list(node, seg, char)
            
            else:
                for seg in result:
                    node = tree.get_node(seg)
                    edit_new_list(node, seg, char)
            
            return recursion_helper(new_list, pat[1:])

    return list(set(recursion_helper([], pattern)))

'''
with open("a_tale_of_two_cities.txt", encoding="utf-8") as f:
    text = f.read()   
tree = word_frequencies(text)  
print(word_filter(tree, 'r?c*t'))
'''



# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
