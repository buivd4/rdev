# Rdev

**Rdev** by **buivd4** is inspired by `auto-rsync`, which makes remote development become easier and faster. With rdev, the remote work directory now is auto-syncing with the local directory. Enjoy coding :D
## Installation
You must install `rsync` and `sshpass` first (automation soon :v).
Git clone this repository then change the directory to the repository.
From the repository, run:
```bash
$ pip install .
```

## Usage
```bash
$ rdev local_directory remote_user@remote_host:remote_path
```

## Example
Create auto-syncing between local directory `/home/user0/Downloads/the-project` and remote directory `/var/www/html` at `my.host.com` using user `root`.
```bash
$ rdev /home/user0/Downloads/the-project root@my.host.com:/var/www/html
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
