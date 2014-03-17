describe("Dependencies", function() {

  it("should be able to check if field value equals dependency value", function() {
    expect(djangoBob.dependencyCondition('aaa', 'aaa')).toBeTruthy();
    expect(djangoBob.dependencyCondition('a', 'b')).not.toBeTruthy();
    expect(djangoBob.dependencyCondition('3', 3)).not.toBeTruthy();
    expect(djangoBob.dependencyCondition({a: 'b'}, {a: 'b'})).toBeTruthy();
    expect(djangoBob.dependencyCondition({a: 'b'}, "{a: 'b'}")).not.toBeTruthy();
    expect(djangoBob.dependencyCondition(false, false)).toBeTruthy();
  });

  it("should always pass field value if dependency value was null", function() {
    expect(djangoBob.dependencyCondition(null, 'aaa')).toBeTruthy();
    expect(djangoBob.dependencyCondition(null, false)).toBeTruthy();
    expect(djangoBob.dependencyCondition(null, null)).toBeTruthy();
    expect(djangoBob.dependencyCondition(null, {a: 'b'})).toBeTruthy();
  });

  it("should match field value to element of dependency value array", function() {
    expect(djangoBob.dependencyCondition([1, 2, 'aaa', 3], 'aaa')).toBeTruthy();
    expect(djangoBob.dependencyCondition([1, 2, 'aaa', 3], false)).not.toBeTruthy();
    expect(djangoBob.dependencyCondition([false, 3], false)).toBeTruthy();
    expect(djangoBob.dependencyCondition([null], null)).toBeTruthy();
    expect(djangoBob.dependencyCondition([null], {a: 'b'})).not.toBeTruthy();
  });

  it("should set value to text field", function () {
    var field = $('<input type="text">');
    djangoBob.setFieldValue(field, "Nobody expects spanish inquisition!");
    expect(field.val()).toEqual("Nobody expects spanish inquisition!");
    djangoBob.setFieldValue(field, "");
    expect(field.val()).toEqual("");
  });

  it("shouldn't change field value if there is try to set null", function () {
    var field = $('<input type="text">');
    djangoBob.setFieldValue(field, "Nobody expects spanish inquisition!");
    expect(field.val()).toEqual("Nobody expects spanish inquisition!");
    djangoBob.setFieldValue(field, null);
    expect(field.val()).toEqual("Nobody expects spanish inquisition!");
  });

  it("should set value to checkbox", function () {
    var field = $('<input type="checkbox">');
    djangoBob.setFieldValue(field, true);
    expect(field.prop("checked")).toBeTruthy();
    djangoBob.setFieldValue(field, false);
    expect(field.prop("checked")).not.toBeTruthy();
  });

  it("should set value and options to selectbox", function () {
    var field = $('<select></select>'),
      values = [1, [
        [1, 'single'], [2, 'widower'], [3, 'married']
      ]],
      options;
    djangoBob.setFieldValue(field, values);
    expect(field.children('[selected="selected"]').val()).toEqual(String(values[0]));
    expect(field.val()).toEqual(String(values[0]));
    options = field.children().map(function (i, el) {
      var $el= $(el);
      return [[parseInt($el.val(), 10), $el.html()]];
    });
    expect(options.toArray()).toEqual(values[1]);
  });
});
