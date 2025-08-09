# process the list of PDF files we want to ingest
with open('data/pdf_list.txt', 'r') as file_list:
    for file in file_list:
        # Clean the url
        url = file.strip().strip('\"')
        title = url.split('/')[-1]

        # check each file against the list of problematic files
        with open('data/problem_files.txt', 'r') as problem_list:
            for problem in problem_list:
                if problem.strip() == title:
                    print(url)
