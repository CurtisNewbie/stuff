# Linux User Group

## Permissions

Permissions include:

- Read
- Write
- Execute

Explaination of `ls -l` output:
 
```sh
-rw-r--r--  1 myboi staff   1.8K May 23 17:37 README.md
```

The first ten chars are the access permissions, these are explained below in order:

```sh
-  rw- r-- r--
1  234 567 890
```

**In General:**

- 1-1: the type of file
- 2-4: owner's rwx permission
- 5-7: members of same group as owner' rwx permission
- 8-10: rwx permissions of all other users
- the number '1' above: number of links
- 'myboi': owner name 
- 'staff': group name
- '1.8K': number of bytes (with -h flag)

**Details:**

1. type of file, in this case it's just a regular file
    - – : regular file.
    - d : directory.
    - c : character device file.
    - b : block device file.
    - s : local socket file.
    - p : named pipe.
    - l : symbolic link.
2. read permission (`r/-`), the file owner has read permission 
3. write permission (`w/-`), the file owner has write permission 
4. execute permission (`x/-`), the file owner doesn't have execute permission 
5. read permission (`r/-`), the members of same group have read permission 
6. write permission (`w/-`), the members of same group doesn't have write permission 
7. execute permission (`x/-`), the members of same group doesn't have execute permission 
8. read permission (`r/-`), other users have read permission 
9. write permission (`w/-`), other users doesn't have write permission 
10. execute permission (`x/-`), other users doesn't have execute permission 

Users are created with their primary group. Then users can be associated with multiple secondary groups (stored in `/etc/groups` file).
Users can only belong to one single primary group, but users can be associated with zero or more secondary groups.

## Commands 

**Return user info, e.g,:**

- uid
- gid
- groups

```sh
id $user 
```

**Return groups of user:**

```sh
groups $user 
```

**Create group:**

```sh
groupadd $groupName
```

**Add user to a secondary group:**

```sh
sudo usermod -aG $someGroup $user  
```

**Create a user:**

```sh
useradd $user
```

**Setup password for user:**

```sh
passwd $user
```

**Change password for current user (interactive):**

```sh
passwd
```

**Delete a user:**

```sh
userdel $name
```

## ref

- https://www.linode.com/docs/guides/linux-users-and-groups/
- https://frameboxxindore.com/linux/what-are-special-files-in-linux.html"
- https://docs.docker.com/engine/install/linux-postinstall/#:~:text=The%20Docker%20daemon%20always%20runs%20as%20the%20root,socket%20accessible%20by%20members%20of%20the%20docker%20group.
