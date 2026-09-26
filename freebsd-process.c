/* Native process queries; no procfs mount or elevated privileges required. */
#include <sys/types.h>
#include <sys/param.h>
#include <sys/sysctl.h>
#include <sys/user.h>
#include <errno.h>
#include <string.h>

#include "freebsd-process.h"

static int
process_info(pid_t pid, struct kinfo_proc *info)
{
	int mib[] = { CTL_KERN, KERN_PROC, KERN_PROC_PID, pid };
	size_t length = sizeof(*info);

	if (pid <= 0) {
		errno = EINVAL;
		return 0;
	}
	memset(info, 0, sizeof(*info));
	if (sysctl(mib, 4, info, &length, NULL, 0) == -1)
		return 0;
	return length == sizeof(*info) && (size_t)info->ki_structsize == sizeof(*info)
	       && info->ki_pid == pid;
}

pid_t
freebsd_parent_pid(pid_t pid)
{
	struct kinfo_proc info;

	return process_info(pid, &info) ? info.ki_ppid : 0;
}

ssize_t
freebsd_executable_path(char *path, size_t capacity)
{
	int mib[] = { CTL_KERN, KERN_PROC, KERN_PROC_PATHNAME, -1 };
	size_t length = capacity;

	if (!path || capacity == 0) {
		errno = EINVAL;
		return -1;
	}
	path[0] = '\0';
	if (sysctl(mib, 4, path, &length, NULL, 0) == -1)
		return -1;
	if (length == 0 || length > capacity || path[length - 1] != '\0'
	    || path[0] != '/') {
		path[0] = '\0';
		errno = EINVAL;
		return -1;
	}
	return (ssize_t)strlen(path);
}

int
freebsd_process_matches(pid_t pid, uid_t uid, pid_t session, const char *name)
{
	struct kinfo_proc info;

	return name && process_info(pid, &info) && info.ki_uid == uid
	       && info.ki_sid == session && strcmp(info.ki_comm, name) == 0;
}
