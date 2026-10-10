// LD_PRELOAD hook: drop the idle heartbeat that app_launcher_linux.cpp
// writes to stderr about once a second:
//   MojoThreadServiceDelegate::PostDealyedTask tid:<n>
// Logging is initialized with LOG_TO_SYSTEM_DEBUG_LOG, so INFO lines reach
// the terminal. The log file write uses a different FILE* and is unchanged.
// Build with -D_GNU_SOURCE so memmem is declared.
#include <dlfcn.h>
#include <stdio.h>
#include <string.h>

namespace {

using FwriteFn = size_t (*)(const void*, size_t, size_t, FILE*);

FwriteFn real_fwrite() {
    static FwriteFn fn = reinterpret_cast<FwriteFn>(dlsym(RTLD_NEXT, "fwrite"));
    return fn;
}

bool is_idle_mojo_heartbeat(const void* ptr, size_t bytes) {
    static const char kNeedle[] = "MojoThreadServiceDelegate::PostDealyedTask tid:";
    const size_t needle_len = sizeof(kNeedle) - 1;
    if (bytes < needle_len) {
        return false;
    }
    return memmem(ptr, bytes, kNeedle, needle_len) != nullptr;
}

}  // namespace

extern "C" size_t fwrite(const void* ptr, size_t size, size_t nmemb, FILE* stream) {
    FwriteFn real = real_fwrite();
    if (real && stream == stderr && ptr && size != 0 && nmemb != 0) {
        size_t bytes = size * nmemb;
        if (bytes / size == nmemb && is_idle_mojo_heartbeat(ptr, bytes)) {
            return nmemb;
        }
    }
    return real ? real(ptr, size, nmemb, stream) : 0;
}
