def format_query_results(query_results, column_names):
    updated_results = []
    for result in query_results:
        new_dict = {k: v for k, v in zip(column_names, result)}
        updated_results.append(new_dict)
    return updated_results
