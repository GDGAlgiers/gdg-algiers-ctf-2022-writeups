class Integer
  def rol k
    (self << k) | (self >> (16-k));
  end
  def stringify
    hex = self.to_s(16)
    hex = ?0 + hex if hex.length.odd?
    hex.each_char.each_slice(2).map{|sl|sl.join.to_i(16).chr}.join
  end
end

16.times do|a1|
  16.times do|a2|
    16.times do|a5|
      16.times do|a6|
        a3 = a1 ^ a5;
        a4 = a2 ^ a6;
        a7 = a1 ^ a3 ^ 3
        a8 = a2 ^ a4 ^ 3
        if a3 ^ a5 == a7
          x0 = (a1 << 12) | (a2 << 4) | 0x700
          x1 = (a3 << 12) | (a4 << 4) | 0x4
          x2 = (a5 << 12) | (a6 << 4) | 0xd02
          x3 = (a7 << 12) | (a8 << 4) | 0x202
          conditions = [
            (x1 ^ x2 ^ 0xf00) & 0xff00 == x3 & 0xff00,
            ((x0 ^ x2).rol(1) ^ 0xf0) & 0xf0f0 == x3 & 0xf0f0,
            x0 ^ x1 ^ 0x3536 == x3,
            (x0 ^ x1) & 0xf0f0 == x2 & 0xf0f0
          ]
          if conditions.all?
            puts "(#{a1}, #{a2}, #{a3}, #{a4}, #{a5}, #{a6}, #{a7}, #{a8})"
            puts "[++] #{[x0, x1, x2, x3].map(&:stringify).join}"
            puts "[++] #{[x0, x1, x2, x3].map(&:stringify).join.each_codepoint.map{|e|e.to_s(16).rjust(2,?0)}.join}"
          end
        end
      end
    end
  end
end
