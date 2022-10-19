import 'dart:io';

void my_wait(int x) {
  sleep(Duration(milliseconds: 50 * x));
}

// code: 246843547418
void main(List<String> args) {
  print("Give me the code: ");
  String? code = stdin.readLineSync();
  if (code!.length == 12) {
    my_wait(2);
    if (code[0] == '2') {
      my_wait(1);
      if (code[1] == '4') {
        my_wait(1);
        if (code[2] == '6') {
          my_wait(1);
          if (code[3] == '8') {
            my_wait(1);
            if (code[4] == '4') {
              my_wait(1);
              if (code[5] == '3') {
                my_wait(1);
                if (code[6] == '5') {
                  my_wait(1);
                  if (code[7] == '4') {
                    my_wait(1);
                    if (code[8] == '7') {
                      my_wait(1);
                      if (code[9] == '4') {
                        my_wait(1);
                        if (code[10] == '1') {
                          my_wait(1);
                          if (code[11] == '8') {
                            my_wait(1);
                            List<int> by73L157 = [
                              6,
                              60,
                              39,
                              32,
                              55,
                              0,
                              55,
                              48,
                              33,
                              44,
                              49,
                              32,
                              54,
                              62,
                              4,
                              26,
                              50,
                              116,
                              97,
                              0,
                              26,
                              8,
                              113,
                              11,
                              26,
                              117,
                              11,
                              38,
                              32,
                              26,
                              97,
                              4,
                              116,
                              1,
                              26,
                              49,
                              116,
                              8,
                              32,
                              26,
                              12,
                              54,
                              26,
                              3,
                              41,
                              113,
                              34,
                              56
                            ];
                            String fl4g = '';
                            for (int i = 0; i < by73L157.length; i++) {
                              fl4g =
                                  fl4g + String.fromCharCode(by73L157[i] ^ 69);
                            }
                            print("correct! here is your flag: ");
                            print(fl4g);
                          } else {
                            print("wrong!");
                          }
                        } else {
                          print("wrong!");
                        }
                      } else {
                        print("wrong!");
                      }
                    } else {
                      print("wrong!");
                    }
                  } else {
                    print("wrong!");
                  }
                } else {
                  print("wrong!");
                }
              } else {
                print("wrong!");
              }
            } else {
              print("wrong!");
            }
          } else {
            print("wrong!");
          }
        } else {
          print("wrong!");
        }
      } else {
        print("wrong!");
      }
    } else {
      print("wrong!");
    }
  } else {
    print("wrong!");
  }
}
