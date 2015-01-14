define(['jquery', 'bob'], function ($, bob) {
    describe("Dependencies", function() {

      it("should set value to text field", function () {
        var field = $('<input type="text">');
        bob.setFieldValue(field, "Nobody expects spanish inquisition!");
        expect(field.val()).toEqual("Nobody expects spanish inquisition!");
        bob.setFieldValue(field, "");
        expect(field.val()).toEqual("");
      });

      it("shouldn't change field value if there is try to set null", function () {
        var field = $('<input type="text">');
        bob.setFieldValue(field, "Nobody expects spanish inquisition!");
        expect(field.val()).toEqual("Nobody expects spanish inquisition!");
        bob.setFieldValue(field, null);
        expect(field.val()).toEqual("Nobody expects spanish inquisition!");
      });

      it("should set value to checkbox", function () {
        var field = $('<input type="checkbox">');
        bob.setFieldValue(field, true);
        expect(field.prop("checked")).toBeTruthy();
        bob.setFieldValue(field, false);
        expect(field.prop("checked")).not.toBeTruthy();
      });

      it("should set value and options to selectbox", function () {
        var field = $('<select></select>'),
          values = [1, [
            [1, 'single'], [2, 'widower'], [3, 'married']
          ]],
          options;
        bob.setFieldValue(field, values);
        expect(field.children(':selected').val()).toEqual(String(values[0]));
        expect(field.val()).toEqual(String(values[0]));
        options = field.children().map(function (i, el) {
          var $el= $(el);
          return [[parseInt($el.val(), 10), $el.html()]];
        });
        expect(options.toArray()).toEqual(values[1]);
      });
    });

    describe("DependencyConditions", function () {
      it("could check if value is empty", function () {
        expect(bob.met("", ["notEmpty"])).not.toBeTruthy();
        expect(bob.met(null, ["notEmpty"])).not.toBeTruthy();
        expect(bob.met(undefined, ["notEmpty"])).not.toBeTruthy();
      });

      it("could check if value is not empty.", function () {
        expect(bob.met(20, ["notEmpty"])).toBeTruthy();
        expect(bob.met("2012-03-06", ["notEmpty"])).toBeTruthy();
        expect(bob.met(false, ["notEmpty"])).toBeTruthy();
        expect(bob.met([1,2,3], ["notEmpty"])).toBeTruthy();
        expect(bob.met({a: '2'}, ["notEmpty"])).toBeTruthy();
      });

      it("could check if single value match exact condition.", function () {
        expect(bob.met("3", ["exact", "3"])).toBeTruthy();
      });

      it("could check if value is converted to string for match condition.", function () {
        expect(bob.met(3, ["exact", "3"])).toBeTruthy();
      });

      it("could check if false match exact condition with false.", function () {
        expect(bob.met(false, ["exact", false])).toBeTruthy();
      });

      it("could check if list value match exact condition.", function () {
        expect(bob.met([5, "3"], ["exact", ["5", "3"]])).toBeTruthy();
      });

      it("could check if value match exact date condition.", function () {
        expect(bob.met(
          new Date(2012, 2, 5),
          ["exact", "2012-03-05"]
        )).toBeTruthy();
      });

      it("could check if wrong date doesn't match exact condition.", function () {
        expect(bob.met(
          new Date(2013, 5, 5),
          ["exact", "2012-03-05"]
        )).not.toBeTruthy();
      });

      it("could check if value doesn't match exact condition.", function () {
        expect(bob.met("3", ["exact", "5"])).not.toBeTruthy();
        expect(bob.met(5, ["exact", "4"])).not.toBeTruthy();
      });

      it("could check if value is any value.", function () {
        expect(bob.met(false, ["any"])).toBeTruthy();
        expect(bob.met(undefined, ["any"])).toBeTruthy();
        expect(bob.met(null, ["any"])).toBeTruthy();
        expect(bob.met(3, ["any"])).toBeTruthy();
        expect(bob.met("3", ["any"])).toBeTruthy();
        expect(bob.met([1,2], ["any"])).toBeTruthy();
        expect(bob.met({a: '3'}, ["any"])).toBeTruthy();
      });

      it("could check if value is member of array.", function () {
        expect(bob.met(3, ["memberOf", ["1", "2", "3"]])).toBeTruthy();
        expect(bob.met("3", ["memberOf", ["1", "2", "3"]])).toBeTruthy();
        expect(bob.met(4, ["memberOf", ["1", "2", "3"]])).not.toBeTruthy();
        expect(bob.met(false, ["memberOf", ["1", false, "3"]])).toBeTruthy();
        expect(bob.met(false, ["memberOf", ["1", "false", "3"]])).not.toBeTruthy();
      });

      it("could check if date is member of array.", function () {
        expect(bob.met(new Date(2012, 2, 7), ["memberOf", ["1", "2012-03-07", "3"]])).toBeTruthy();
        expect(bob.met("2012-03-05", ["memberOf", ["1", "2012-03-05", "3"]])).toBeTruthy();
        expect(bob.met(new Date(2012, 2, 5), ["memberOf", ["1", "2012-03-07", "3"]])).not.toBeTruthy();
        expect(bob.met("2011-05-07", ["memberOf", ["1", "2012-03-07", "3"]])).not.toBeTruthy();
      });
    });
});
