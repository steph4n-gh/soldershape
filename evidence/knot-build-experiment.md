# Ridgerunner baseline experiment

Status on October 16, 2026. The numerical gate remains unqualified. No Ridgerunner tightening run, tube export, or physical validation completed.

The checkout is pinned to `4ee3199e737dcd3580d8bfc5deb031cd53f5f554`. The downloaded archives match the hashes recorded in `REPORT.md` and the upstream Homebrew formulas.

## Native results

`./autogen.sh` fails because macOS lacks `autoreconf`. The failure is preserved in `bootstrap.log`.

The generated configure script in release 2.3.1 starts successfully with Clang. It stops at `pkg-config openblas`. The failure is preserved in `configure.log`.

## Isolated Linux results

The existing `ubuntu:24.04` image ran under Docker with only this investigation directory mounted at `/work`. No macOS dependencies were installed. The container was removed automatically when its command stopped.

Ubuntu packages supplied GCC, autotools, GSL, argtable2, OpenBLAS, LAPACKE, and ncurses. `plCurve` 11.2.2 bootstrapped, configured, built, and installed under `/work/linux-prefix` successfully. `tsnnls` 2.5.1 bootstrapped and configured. Its library compiled, but its test executable failed to link against four LAPACKE symbols.

The decisive error in `tsnnls-build.log` is:

```text
/usr/bin/ld: ./.libs/libtsnnls.so: undefined reference to `LAPACKE_dgecon_work'
/usr/bin/ld: ./.libs/libtsnnls.so: undefined reference to `LAPACKE_dpocon_work'
/usr/bin/ld: ./.libs/libtsnnls.so: undefined reference to `LAPACKE_dgetrf_work'
/usr/bin/ld: ./.libs/libtsnnls.so: undefined reference to `LAPACKE_dpotrf'
collect2: error: ld returned 1 exit status
```

The observed link command uses `-lopenblas` without `-llapacke`. The installed Ubuntu OpenBLAS does not resolve those LAPACKE entry points through that command. A likely repair is adding `LIBS=-llapacke` to the tsnnls configure command. That repair was not attempted because the parent comparison already favored the other candidate and this investigation was bounded. The source was not patched.

This build integration failure does not establish that the optimizer fails on a knot. The failure occurred before Ridgerunner could build. It establishes that a zero-setup browser port is not a small verified substitution on this host.

## Reproduction

From `/Volumes/Storage/oct16project/.research/knot`, with the recorded archives already unpacked, run:

```sh
docker run --rm \
  -v /Volumes/Storage/oct16project/.research/knot:/work \
  -w /work ubuntu:24.04 sh /work/build-baseline.sh
```

This reproduces the initial command sequence and writes the same log paths. The system package versions follow Ubuntu's package repositories. The three numerical source archive versions and hashes are pinned. The original command used the same shell steps inline. `build-baseline.sh` preserves those steps in a reviewable file.

The intended next numerical command, after resolving dependencies, is:

```sh
ridgerunner -a -r 5 -s 1000 3.1.vect
```

That command has not run here. A valid qualification would inspect the final VECT and logs, evaluate residual and thickness, compare against the starting geometry, repeat on the figure-eight, and preserve a deliberately problematic symmetric case. A completed step budget alone would not demonstrate convergence.
