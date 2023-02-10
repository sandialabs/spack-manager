# Convenience function for running clang-format
function run-nalu-clang-format()
{
spack cd -s nalu-wind
cf=/projects/wind/core-spack-manager/scripts/admin-system-setup/compilers_store/linux-rhel7-x86_64/gcc-12.2.0/llvm-13.0.1-bzlmdor3cuyofkkukjhqfyts5ningcmc/bin/clang-format
find . -path 'wind-utils' -prune -iname "*.h" -o -iname "*.C" | xargs ${cf} -i
}

