# Reviewed upstream runtime notes

Merged from ljagiello/ctf-skills c332c7be1b27cb64639a20124ac55ba916adef92 (MIT), retrieved 2026-10-01. Incorrect recipes were replaced, not copied into the solving path. See the correction ledger.

## Largebin insertion prerequisites

Choose the supplied allocator's exact source and debug the insertion branch. A largebin insertion write requires a reachable metadata corruption, the appropriate chunk sizes/order and the branch's consistency checks. It is not a universal arbitrary-value write. Preserve measured offsets; verify the actual pointer value written with a harmless local target. Never use __free_hook as a current universal destination; normal hook support was removed in glibc 2.34. Fill a tcache bin to divert eligible frees; draining it creates capacity. Tiny freed chunks may go to fastbins, rather than unsorted.

## glibc 2.39 tcache layout and calloc

The [2.39 allocator source](https://raw.githubusercontent.com/bminor/glibc/glibc-2.39/malloc/malloc.c) has uint16_t counts and raw entries heads. Freed entries contain a safe-linked next pointer and a plain random key. Seven is the default tunable count, not an immutable limit. Its calloc path uses _int_malloc rather than taking entries directly from tcache; internal allocation can still populate caches. malloc/free/malloc/free is ordinary reuse, not a double-free bypass. A second free writes/checks fresh bookkeeping; calloc zeroing does not automatically defeat it. Derive an exploit from the actual UAF/write primitive and reproduce locally.

## House of Tangerine: research routing

The imported count-underflow/largebin recipe was unsupported and conflated allocator families. Search an exact-version primary how2heap demonstration before adopting this name. Preserve the useful idea of examining top-chunk size corruption and sysmalloc-triggered frees when ordinary UAF is absent. Record alignment, page boundary, size constraints and safe-linking requirements from that demonstration; stop if the binary lacks the primitive. [Heap variants](heap-techniques-2.md) contain separate challenge-derived paths.

## CET shadow stack and IBT

Distinguish enforced shadow stacks from IBT, ELF properties from runtime activation, and challenge-patched implementations from stock kernels. Linux [shadow-stack documentation](https://docs.kernel.org/arch/x86/shstk.html) describes a verified shadow-stack signal token and restricted mappings. An ordinary writable fake sigreturn frame does not grant arbitrary SSP control. The earlier fixed SSP offset and writable fake-stack recipe were unsupported. Inspect loader/kernel settings and target call paths; prefer a proven allowed indirect call, data-only corruption or an implementation-specific flaw. Reproduce in the supplied VM without modifying the host kernel.

## io_uring PBUF_RING lifetime: CVE-2024-0582 lead

Keep this lead for dedicated challenge kernels only. Identify the exact registration/mmap/unregistration lifetime and patch in the supplied build; the imported generic PROVIDE_BUFFERS race and guessed cred spray are not a validated exploit. Preserve a local crash/minimal lifetime trace before escalating the analysis. A CVE number and a kernel version substring are insufficient evidence of applicability. Do not exercise kernel primitives on the operator host or a shared organizer node.
