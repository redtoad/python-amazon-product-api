#!/usr/bin/env python
import gtk

from config import AWS_KEY, SECRET_KEY
from amazonproduct import API

class BrowseNodeExplorer (gtk.Window):
    
    """
    Gtk explorer for Amazon BrowseNodes.
    """
    
    def on_delete(self, widget, event, data=None):
        # closes the window and quits.
        gtk.main_quit()
        return False
    
    def on_tree_click(self, widget, event, data=None):
        # if double click
        if event.type == gtk.gdk._2BUTTON_PRESS:
            
            # get data from highlighted selection
            treeselection = self.treeview.get_selection()
            model, iter = treeselection.get_selected()
            name_of_data = self.treestore.get_value(iter, 0)
            
            # and fetch selected node
            self.fetch_nodes(name_of_data)
            
    def __init__(self):
        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title("BrowseNode Explorer")
        self.set_size_request(400, 200)
        self.connect("delete_event", self.on_delete)
        
        self.api = API(AWS_KEY, SECRET_KEY)
        
        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(int, str)
        
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)
        
        # add column id
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('id', renderer, text=0)
        self.treeview.append_column(column)
        
        # add column name
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn('name', renderer, text=1)
        column.set_sort_column_id(0) # Allow sorting on the column
        self.treeview.append_column(column)
        
        # make it clickable
        self.treeview.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.treeview.connect('button_press_event', self.on_tree_click)
        
        scrolled = gtk.ScrolledWindow()
        scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled.add(self.treeview)
        
        self.add(scrolled)
        self.show_all()
        
    def fetch_nodes(self, node_id):
        """
        Fetches a BrowseNode from Amazon.
        """
        self.treestore.clear()
        
        root = self.api.browse_node_lookup(node_id)
        node = root.BrowseNodes.BrowseNode
        id = node.BrowseNodeId.pyval
        try:
            is_root = node.IsCategoryRoot.pyval == 1
        except AttributeError:
            is_root = False
        name = node.Name.pyval
        
        try:
            parents = dict((parent.BrowseNodeId.pyval, parent.Name.pyval)
                        for parent in node.Ancestors.BrowseNode)
        except AttributeError:
            parents = {}
            
        try:
            children = dict((child.BrowseNodeId.pyval, child.Name.pyval)
                        for child in node.Children.BrowseNode)
        except AttributeError:
            children = {}
        
        piter = None
        for parent_id, parent_name in parents.items():
            piter = self.treestore.append(None, [parent_id, parent_name])
            
        iter = self.treestore.append(piter, [id, name])
            
        for child_id, child_name in children.items():
            self.treestore.append(iter, [child_id, child_name])
            
        self.treeview.expand_all()
        
    def main(self):
        gtk.main()

if __name__ == "__main__":
    explorer = BrowseNodeExplorer()
    explorer.fetch_nodes(542676) # Music node for locale de
    # a list of root nodes can be found here:
    # http://docs.amazonwebservices.com/AWSECommerceService/2009-11-01/DG/index.html?BrowseNodeIDs.html
    explorer.main()
