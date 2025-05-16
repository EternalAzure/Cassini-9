import glob
from pathlib import Path



def find_nc_file(filename:str) -> Path:
    """Takes filename, partial or full path and find correct file from data-folder."""
    print(f"\nSearching {filename=}")

    #dir_path = os.path.dirname(os.path.realpath(__file__))
    netcdf_files = [Path(file).absolute() for file in glob.glob(f"data/netcdf/*/*/*.nc")]
    filepath = Path(filename).with_suffix(".nc")

    if filepath.is_absolute():
        # 1) Absolute and found
        if filepath in netcdf_files: return filepath
        # 2) Absolute and not found
        else:
            print("Filepath not found in data/netcdf -folder")
            filename = input("Please give another filename: ")
            return find_nc_file(filename)
    
    if filepath.parent == Path("."):
        matches = [file for file in netcdf_files if file.name == filepath.name]
        if len(matches) > 1:
            # 3) Can't specify which file
            print(f"Found multiple files with the same name:")
            for match in matches:
                print(match)
            filename = input("Please give another filename: ")
            return find_nc_file(filename)
        elif matches: 
            # 4) Found match for ambiguous name
            print("Found only one file matching name:")
            print(f"{matches[0]}")
            confirmation = input("Is this correct file? (y/n): ").lower()
            if confirmation == "y" or confirmation == "yes":
                return matches[0]
            else:
                # 5) User rejected the match
                print("Try one of these:")
                for file in netcdf_files[:20]:
                    print(file)
                filename = input("Please give another filename: ")
                return find_nc_file(filename)
    
    matches = [file for file in netcdf_files if str(file).endswith(str(filepath))]
    if len(matches) > 1:
        # 6) Found multiple files
        print(f"Found multiple files with the same name:")
        for match in matches:
            print(match)
        filename = input("Please give more specific name: ")
        return find_nc_file(filename)
    if matches:
        # 7) Found one match
        return matches[0]
    
    print("No matches found.")
    print("Try one of these:")
    for file in netcdf_files[:20]:
        print(file)
    filename = input("Please give more specific name: ")
    return find_nc_file(filename)