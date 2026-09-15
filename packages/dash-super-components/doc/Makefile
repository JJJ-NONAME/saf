# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    = -j auto -W --keep-going
SPHINXBUILD   = sphinx-build
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# Customized clean due to examples gallery
clean:
	rm -rf $(BUILDDIR)
	rm -rf $(SOURCEDIR)/sg_execution_times.rst
	rm -rf $(SOURCEDIR)/examples
	find . -type d -name "_autosummary" -exec rm -rf {} +

# Customized pdf for svg format images
pdf:
	exit 0
# To enable when the doc is compatible with the pdf generation
# 	@$(SPHINXBUILD) -M latex "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
# 	cd $(BUILDDIR)/latex && latexmk -r latexmkrc -pdf *.tex -interaction=nonstopmode || true
# 	(test -f $(BUILDDIR)/latex/*.pdf && echo pdf exists) || exit 1
