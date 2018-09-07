## Git subtree to sync with ipyjulia_core
CORE_REPO = ipyjulia_core
CORE_PATH = src/replhelper/core

.PHONY: *-core

sync-core: push-core
	$(MAKE) pull-core
# Doing push first so that it fails if the local and remote are
# incompatible.  It means that the core is updated elsewhere.  In that
# case, I need to handle it manually (e.g., maybe non-squash pull).

push-core:
	git subtree push --prefix $(CORE_PATH) $(CORE_REPO) master

pull-core:
	git subtree pull --prefix $(CORE_PATH) $(CORE_REPO) master --squash

set-remote-core:
	git remote add -f $(CORE_REPO) git@github.com:tkf/ipyjulia_core.git
