#ifndef FREEBSD_PROCESS_H
#define FREEBSD_PROCESS_H

#include <stddef.h>
#include <sys/types.h>

pid_t freebsd_parent_pid(pid_t pid);
ssize_t freebsd_executable_path(char *path, size_t capacity);
int freebsd_process_matches(pid_t pid, uid_t uid, pid_t session, const char *name);

#endif
