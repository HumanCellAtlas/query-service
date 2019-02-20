from query.lib.db.database import Tables


class LinksFileTransform:

    @classmethod
    def links_file_transformer(cls, tables, links):
        for link in links:
            process = cls.format_process_info(link)
            process['children'] = list(cls.get_child_process_uuids(tables, process['output_file_uuids']))
            process['parents'] = list(cls.get_parent_process_uuids(tables, process['input_file_uuids']))

            cls.create_processes(tables, process)
            cls.link_parent_and_child_processes(tables, process)

    @classmethod
    def format_process_info(cls, link):
        process_uuid = str(link['process'])
        protocol_uuids = []
        for protocol in link['protocols']:
            protocol_uuid = protocol['protocol_id']
            protocol_uuids.append(protocol_uuid)

        return {"process_uuid": process_uuid, "input_file_uuids": link["inputs"], "output_file_uuids": link["outputs"],
                "protocol_uuids": protocol_uuids}

    @classmethod
    def get_file_type(cls, file_uuid):
        # TODO implement this or remove file_type column from table
        return 'file_type'

    @classmethod
    def get_child_process_uuids(cls, tables: Tables, output_file_uuids):
        children = []
        for file_uuid in output_file_uuids:
            child_uuids = tables.process_links.list_process_uuids_for_file_uuid(file_uuid, 'INPUT_ENTITY')

            children = children + child_uuids
        return list(set(children))

    @classmethod
    def get_parent_process_uuids(cls, tables: Tables, input_file_uuids):
        parents = []
        for file_uuid in input_file_uuids:
            parent_uuids = tables.process_links.list_process_uuids_for_file_uuid(file_uuid, 'OUTPUT_ENTITY')
            parents = parents + parent_uuids
        return list(set(parents))

    @classmethod
    def create_processes(cls, tables, process):
        input_file_uuids = process['input_file_uuids']
        output_file_uuids = process['output_file_uuids']
        protocol_uuids = process['protocol_uuids']

        for file_uuid in input_file_uuids:
            file_type = cls.get_file_type(file_uuid)
            tables.process_links.insert(process['process_uuid'], file_uuid, 'INPUT_ENTITY', file_type)

        for file_uuid in output_file_uuids:
            file_type = cls.get_file_type(file_uuid)
            tables.process_links.insert(process['process_uuid'], file_uuid, 'OUTPUT_ENTITY', file_type)

        for file_uuid in protocol_uuids:
            file_type = cls.get_file_type(file_uuid)
            tables.process_links.insert(process['process_uuid'], file_uuid, 'PROTOCOL_ENTITY', file_type)

    @classmethod
    def link_parent_and_child_processes(cls, tables: Tables, process: object):
        already_linked_parents = tables.process_links.list_direct_parent_process_uuids(process['process_uuid'])
        already_linked_children = tables.process_links.list_direct_children_process_uuids(process['process_uuid'])

        parents = [x for x in process['parents'] if x not in already_linked_parents]
        children = [x for x in process['children'] if x not in already_linked_children]

        for parent in parents:
            tables.process_links.insert_parent_child_link(parent_process_uuid=parent,
                                                          child_process_uuid=process['process_uuid'])
        for child in children:
            tables.process_links.insert_parent_child_link(parent_process_uuid=process['process_uuid'],
                                                          child_process_uuid=child)
