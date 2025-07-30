from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.tables import Table

from sphinx.locale import _
from bs4 import BeautifulSoup as bs

import re

from sphinx.locale import _
from TexSoup import TexSoup

def align(argument):
    return directives.choice(argument, ('left', 'center', 'right'))

class HTMLTableDirective(Table):

    option_spec = Table.option_spec.copy()
#    option_spec = {'header-rows': directives.nonnegative_int,
#                'stub-columns': directives.nonnegative_int,
#                'width': directives.length_or_percentage_or_unitless,
#                'widths': directives.value_or(('auto', ),
#                                                directives.positive_int_list),
#                'class': directives.class_option,
#                'name': directives.unchanged,
#                'align': align} 
    option_spec.update({
            'header-rows' : directives.unchanged,
    })

    def run(self):

        col_widths = []

        title, messages = self.make_title()

        html_table_text = self.block_text.split('\n\n')[-1].strip(' ')
        
        table_soup = bs(html_table_text,"html.parser")
        table_head = table_soup.find('thead')

        total_rows = table_soup.find_all('tr')
        max = 0
        for row in total_rows:
            num_cols = len(row.find_all('td'))
            if num_cols >= max:
                max = num_cols

        table = nodes.table()

        tgroup = nodes.tgroup()
        table += tgroup

        for i in range(max):
            colspec = nodes.colspec(colwidth=1)
            tgroup += colspec

        num_head_rows = len(table_soup.find('thead').find_all('tr'))

        rows = []

        # parse the body of the table:
        body_rows = table_soup.find('tbody').find_all('tr')

        for row in body_rows:
            row_node = nodes.row()
            cell_list = row.find_all('td')
            for cell in cell_list:
                entry = nodes.entry()
                entry += nodes.raw(None,cell.text,format='html')
                row_node += entry
            rows.append(row_node)


        if table_head != None:
            th_rows = []
            table_head_rows = table_head.find_all('tr')

            for row in table_head_rows:
                row_node = nodes.row()
                cell_list = row.find_all('th')
                for cell in cell_list:
                    cell_text = nodes.raw(None,cell.text)
                    cell_text_node = nodes.Element()
                    self.state.nested_parse(cell_text, 0, cell_text_node)
                    aux = nodes.Text('')
                    aux.children = cell_text_node.children
                    cell_text_node = aux
                    attrs = {}
                    if len(cell.attrs) > 0:
                        for key,value in cell.attrs.items():
                            if key == 'colspan':
                                attrs['morecols']=int(value)-1
                            if key == 'rowspan':
                                attrs['morerows']=int(value)-1
                            else:
                                attrs[key] = str(value)

                    node_entry = nodes.entry(**attrs)
                    node_entry += cell_text_node
                    row_node += node_entry

                th_rows.append(row_node)

            rows = th_rows + rows
            thead = nodes.thead()
            thead.extend(rows[:num_head_rows])
            tgroup += thead

        tbody = nodes.tbody()
        tbody.extend(rows[num_head_rows:])
        tgroup += tbody

        if 'align' in self.options:
            table['align'] = self.options.get('align')
        table['classes'] += self.options.get('class', [])
        self.set_table_width(table)
        self.add_name(table)

        if title:
            table.insert(0,title)

        table_node = nodes.raw(None, html_table_text)
        return [table]
        #return [table]+messages

def visit_htmltable_node(self, node):
    pass

def depart_htmltable_node(self, node):
    pass

class LaTeXTableDirective(Table):
    
    RE_MULTICOL = re.compile(r'\\multicolumn{([0-9]+)}{(c|l|r)}{([^}]+)(})')
    RE_MULTIROW = re.compile(r'\\multirow{([0-9]+)}{(c|l|r)}{([^}]+)(})')

    #option_spec = Table.option_spec.copy()
    option_spec = {'header-rows': directives.nonnegative_int,
                'stub-columns': directives.nonnegative_int,
                'width': directives.length_or_percentage_or_unitless,
                'widths': directives.value_or(('auto', ),
                                                directives.positive_int_list),
                'class': directives.class_option,
                'name': directives.unchanged,
                'align': align} 

    def run(self):
        env = self.state.document.settings.env
        builder_name = env.app.builder.name

        if builder_name == 'latex':
            return self.run_latex()
        else:
            return self.run_html()

    def run_latex(self):
        title, messages = self.make_title()

        header_rows = self.options.get('header-rows', 0)

        table_text = self.block_text.split('\n\n')[-1].strip(' ')

        table_soup = TexSoup(table_text)
        tabular = table_soup.find('tabular')
        args = str(tabular.args).strip('{}')

        table_contents = "".join(str(content) for content in tabular.contents[1:])

        table_rows = table_contents.split('\\\\')

        max_num_cols = len(args)

        table = nodes.table()

        attrs = {'colwidth': 1}
        tgroup = nodes.tgroup()
        table += tgroup

        for i in range(max_num_cols):
            colspec = nodes.colspec(**attrs)
            tgroup += colspec

        # Parse the body of the table:
        body_rows = table_rows[header_rows:-1]
        rows = self.parse_rows(body_rows, args, 'latex')

        # Parse the header rows:
        if header_rows != 0:
            th_rows_list = table_rows[:header_rows]
            th_rows = self.parse_rows(th_rows_list, args, 'latex')

            rows = th_rows + rows
            thead = nodes.thead()
            thead.extend(rows[:header_rows])
            tgroup += thead

        tbody = nodes.tbody()
        tbody.extend(rows[header_rows:])
        tgroup += tbody

        self.set_table_width(table)
        self.add_name(table)

        table['classes'] += self.options.get('class', [])
        if title:
            table.insert(0, title)

        return [table] + messages

    def run_html(self):

        title, messages = self.make_title()

        header_rows = self.options.get('header-rows')

        if header_rows == None:
            header_rows = 0

        table_text = self.block_text.split('\n\n')[-1].strip(' ')

        table_soup = TexSoup(table_text)
        tabular = table_soup.find('tabular')
        args = str(tabular.args).strip('{}')

        table_contents = "".join(str(content) for content in tabular.contents[1:])

        table_rows = table_contents.split('\\\\')

        max_num_cols = len(args)

        table = nodes.table()

        attrs = {'colwidth' : 1 }
        tgroup = nodes.tgroup()
        table += tgroup

        for i in range(max_num_cols):

            colspec = nodes.colspec(**attrs)
            tgroup += colspec

        # parse the body of the table:
        body_rows = table_rows[header_rows:-1]
        rows = self.parse_rows(body_rows,args)

        # parse the header rows:
        if header_rows != 0:
            th_rows_list = table_rows[:header_rows]
            th_rows = self.parse_rows(th_rows_list,args)

            rows = th_rows + rows
            thead = nodes.thead()
            thead.extend(rows[:header_rows])
            tgroup += thead

        tbody = nodes.tbody()
        tbody.extend(rows[header_rows:])
        tgroup += tbody

        if 'align' in self.options:
            table['align'] = self.options.get('align')
        table['classes'] += self.options.get('class', [])
        self.set_table_width(table)
        self.add_name(table)

        if title:
            table.insert(0,title)

        return [table]+messages

    def parse_rows(self,row_list : list,table_args: str, builder: str = 'html') -> list:

        rows = []
        for row in row_list:
            row_node = nodes.row()
            cell_list = row.split('&')
            i=0
            for cell in cell_list:

                col_align = 'cell-text-left'  # Default value
                align_arg = table_args[i]
                attrs = {}
                cell_text = str(cell)
                cell_text = cell_text.strip(' ')

                # Search for multi columns
                cell_entry_properties = self.RE_MULTICOL.match(cell_text)
                
                if cell_entry_properties != None:
                    colspan = cell_entry_properties.groups()[0]
                    cell_align = cell_entry_properties.groups()[1]
                    if cell_align != align_arg:
                        align_arg = cell_align
                    cell_text = cell_entry_properties.groups()[2]
                    attrs['morecols']=int(colspan)-1
                
                match align_arg:
                    case 'r': 
                        col_align = 'cell-text-right'
                    case 'c':
                        col_align = 'cell-text-center'
                    case 'l':
                        col_align = 'cell-text-left'

                # TODO
                # Search for multi row


                if builder == 'html':
                    cell_text = nodes.raw(None, cell_text)
                    cell_text_node = nodes.Element()
                    self.state.nested_parse(cell_text, 0, cell_text_node)

                    aux = nodes.Text('')
                    aux.children = cell_text_node.children
                    cell_text_node = aux
                elif builder == 'latex':
                    cell_text_node = nodes.raw(None, cell_text, format='latex')

                entry = nodes.entry()
                for attr, value in attrs.items():
                    entry[attr] = value
                entry['classes'].append(col_align)
                entry += cell_text_node
                row_node += entry
                i+=1

            rows.append(row_node)

        return rows



def setup(app):

    app.add_directive('htmltable',HTMLTableDirective)

    app.add_directive('latextable', LaTeXTableDirective)


    return {
        'version': '0.1.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
