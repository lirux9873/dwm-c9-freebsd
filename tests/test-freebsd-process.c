/* Run natively; this tests actual sysctl/process behavior, not mocked data. */
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <assert.h>
#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include "freebsd-process.h"

int
main(void)
{
	char path[PATH_MAX], tiny[1], *name;
	struct stat st;
	pid_t child;
	int ready[2], status;
	char marker;
	ssize_t length;

	assert(freebsd_parent_pid(getpid()) == getppid());
	assert(freebsd_parent_pid(-1) == 0);
	assert(freebsd_parent_pid(0) == 0);
	assert(!freebsd_process_matches(-1, getuid(), getsid(0), "c9-proc-test"));
	length = freebsd_executable_path(path, sizeof(path));
	assert(length > 0 && (size_t)length == strlen(path));
	assert(path[0] == '/' && stat(path, &st) == 0 && S_ISREG(st.st_mode));
	assert(freebsd_executable_path(tiny, sizeof(tiny)) == -1);
	assert(freebsd_executable_path(NULL, 0) == -1 && errno == EINVAL);
	name = strrchr(path, '/') + 1;
	assert(freebsd_process_matches(getpid(), getuid(), getsid(0), name));
	assert(!freebsd_process_matches(getpid(), getuid(), getsid(0), "wrong-name"));
	assert(!freebsd_process_matches(getpid(), getuid(), (pid_t)-1, name));

	assert(pipe(ready) == 0);
	child = fork();
	assert(child >= 0);
	if (child == 0) {
		close(ready[0]);
		if (setsid() == -1 || write(ready[1], "x", 1) != 1)
			_exit(1);
		close(ready[1]);
		/* Ensure a failing parent does not leave an indefinitely waiting child. */
		alarm(10);
		pause();
		_exit(0);
	}
	close(ready[1]);
	assert(read(ready[0], &marker, 1) == 1);
	close(ready[0]);
	assert(freebsd_parent_pid(child) == getpid());
	assert(!freebsd_process_matches(child, getuid(), getsid(0), name));
	assert(freebsd_process_matches(child, getuid(), child, name));
	assert(kill(child, SIGTERM) == 0);
	assert(waitpid(child, &status, 0) == child);
	assert(freebsd_parent_pid(child) == 0);
	puts("FreeBSD native process tests passed");
	return 0;
}
