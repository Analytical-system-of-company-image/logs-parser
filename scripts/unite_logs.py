import gzip
import os
import shutil
import tarfile
import sys
import click


@click.command()
@click.argument('dirname', type=click.Path())
@click.option('--filename', '-f', help="Output file name", default=os.path.abspath(__file__) + "output.log", type=click.Path())
def main(dirname: str, filename: str = "") -> None:
    """extract all logs into filename logfile"""
    processing(dirname, filename)


def write_to_file(filepath: str, data: bytes) -> None:
    if not os.path.exists(filepath):
        os.mknod(filepath)
    with open(filepath, 'ab') as f:
        f.write(data)
        f.close()


def processing(dirname: str, filename: str) -> None:
    arr = os.listdir(dirname)
    click.echo(f"Opened {dirname}")
    click.echo("Extracting files")
    for i in arr:
        if i.endswith('gz'):
            in_name = f"{dirname}/{i}"
            click.echo(f"Extracting xz {in_name}/{i}")
            out_name = in_name.replace(".gz", "")
            with gzip.open(in_name, 'rb') as f_in:
                with open(out_name, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            click.echo(f"Reading logs from file {out_name}/{i}")
            for line in open(out_name):
                content = bytes(line, 'utf-8')
                write_to_file(filename, content)
            os.remove(out_name)
            click.echo(f"Removed file by path {out_name}")
        elif i.endswith('xz'):
            file = tarfile.open(f"{dirname}/{i}", 'r:xz')
            click.echo(f"Extracting xz {dirname}/{i}")
            file.extractall(dirname)
            next_folder_name = f"{dirname}/{file.members[0].name}"
            file.close()
            processing(next_folder_name, filename)
            shutil.rmtree(next_folder_name)
            click.echo(f"Removed folder by path {next_folder_name}")
        elif "log" in i:
            click.echo(f"Reading logs from file {dirname}/{i}")
            with open(f"{dirname}/{i}", 'rb') as f:
                content = f.read()
                write_to_file(filename, content)


if __name__ == '__main__':
    main()
