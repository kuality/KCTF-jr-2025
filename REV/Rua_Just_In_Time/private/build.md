cargo clean
cargo update
export CC=musl-gcc
export RUSTFLAGS="-C target-feature=+crt-static -C debuginfo=2"
cargo build --release --target x86_64-unknown-linux-musl
./target/x86_64-unknown-linux-musl/release/Rua_Just_In_Time \
  kctf-jr{2ba0fc74c0db3117617f5343f7269ce7612324b541c881f53ac2693812c1884b}
