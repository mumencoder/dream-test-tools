
#define A(X) "a" + ## X

/proc/main()
    LOG(A(A("b")))